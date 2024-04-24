import logging
import re
from typing import Optional

from django.db.models import QuerySet
from django.db import transaction

from courses.models import Subscribe, PaymentMethod, SubscribeState
from payment.models import Payment, SubscriptionPayment
from payment.models.choices import State, CreditDebit, Type

log = logging.getLogger("payment")

USI_PREFIX = "USI-"
# also accept USL since I is often typed as L
RE_USI_STRICT = re.compile(r"[USILusil]{3}[\- _]*(?P<usi>[a-zA-Z0-9]{6})")


class PaymentProcessor:
    @staticmethod
    def process_payments(queryset=None) -> None:
        """
        This method performs the following steps:
        - Detect irrelevant payments
        - Matches payments
        - Mark subscriptions as paid
        - Finalizes payments
        """
        queryset = queryset or Payment.objects.select_for_update()
        with transaction.atomic():
            PaymentProcessor._detect_irrelevant_payments(queryset)
            PaymentProcessor.match_payments(queryset)
            PaymentProcessor.mark_subscriptions_as_paid(queryset)
            PaymentProcessor.finalize_payments(queryset)

    @staticmethod
    def _detect_irrelevant_payments(queryset=Payment.objects) -> None:
        """Sets all new DEBIT transactions as irrelevant payments"""
        new_payments = queryset.filter(
            state=State.NEW, credit_debit=CreditDebit.DEBIT
        ).all()

        for payment in new_payments:
            payment.type = Type.IRRELEVANT
            payment.save()

    @staticmethod
    def match_payments(queryset=Payment.objects) -> None:
        """Tries to match payments to Subscriptions and creates a SubscriptionPayment for each"""
        new_payments = queryset.filter(
            state=State.NEW, credit_debit=CreditDebit.CREDIT
        ).all()

        for payment in new_payments:
            subscription_ids = (
                PaymentProcessor.try_to_get_unique_subscription_identifiers(payment)
            )
            if not subscription_ids:
                payment.state = State.MANUAL
                payment.save()
                continue

            # We found subscription ids, so it must be a subscription payment
            payment.type = Type.SUBSCRIPTION_PAYMENT
            payment.save()

            remaining_amount = payment.amount

            # Try to create a subscription payment for each subscription_id
            for subscription_id in subscription_ids:
                subscription_query = Subscribe.objects.filter(
                    usi__iexact=subscription_id
                )

                num_subscriptions = subscription_query.count()
                if num_subscriptions > 1:
                    # should never happen since USI is unique
                    log.error(
                        f"Implementation Error: Payment {payment} is not related to a unique Subscription"
                    )
                    continue

                if num_subscriptions == 0:
                    # USI was probably misspelled by user
                    log.warning(
                        "USI {0} was not found for payment {1}.".format(
                            subscription_id, payment
                        )
                    )
                    continue

                # Now we know there is exactly one subscription
                matched_subscription: Subscribe = subscription_query.get()

                # Only confirmed subscriptions should be paid
                if matched_subscription.state != SubscribeState.CONFIRMED:
                    log.warning(
                        f"The state of {matched_subscription} is something other than confirmed. "
                        f"Got: {matched_subscription.state}"
                    )
                    payment.state = State.MANUAL
                    payment.save()
                    continue

                # Prevent duplicate (Payment,Subscribe) pairs in SubscriptionPayment
                if SubscriptionPayment.objects.filter(payment=payment, subscription=matched_subscription).exists():
                    log.warning(
                        f"Attempted insertion of duplicate ({payment},{matched_subscription}) pair in SubscriptionPayment."
                    )
                    payment.state = State.MANUAL
                    payment.save()
                    continue

                to_pay = matched_subscription.price_after_reductions()

                # Amount credited to subscription can be at most as much as the remaining amount.
                # Whether the paid amount is sufficient is checked during PaymentProcessor._check_balance(payment)
                amount = min(to_pay, remaining_amount)
                remaining_amount -= amount
                SubscriptionPayment.objects.create(
                    payment=payment, subscription=matched_subscription, amount=amount
                )
                log.info(
                    "Matched payment {0} to subscription {1}".format(
                        payment, subscription_query
                    )
                )

            # Check balance -> this sets state of subscription payment (MATCHED, REIMBURSE, MANUAL)
            PaymentProcessor._check_balance(payment)

    @staticmethod
    def try_to_get_unique_subscription_identifiers(
        payment: Payment,
    ) -> Optional[list[str]]:
        if (
            not payment.remittance_user_string
        ):  # FYI: remittance translates to Überweisung (german)
            log.warning(f"No user remittance was found for payment {payment}.")
            return None

        # Try to get the unique subscription identifier from the remittance user string
        log.info(f"Got remittance_user_string: {payment.remittance_user_string}")
        matches = RE_USI_STRICT.findall(payment.remittance_user_string)

        # if no matches, try removing all spaces first
        if not matches:
            matches = RE_USI_STRICT.findall(
                payment.remittance_user_string.replace(" ", "")
            )

        # giving up on getting the identifier
        if not matches:
            log.warning(f"No USI was recognized in payment {payment}.")
            return None

        # There could be potentially many subscription identifiers for one payment
        # Convert to lowercase, since values are stored as lowercase in database (postgres is case sensitiv)
        subscription_ids = [subscription_id for subscription_id in matches]
        log.info(
            f"Found the following subscription id(s): {', '.join(subscription_ids)}"
        )
        return subscription_ids

    @staticmethod
    def mark_subscriptions_as_paid(queryset=Payment.objects) -> None:
        for payment in queryset.all():
            for s in payment.subscriptions.all():
                if s.open_amount().is_zero():
                    s.mark_as_paid(PaymentMethod.ONLINE)

    @staticmethod
    def finalize_payments(queryset=Payment.objects) -> None:
        """Mark matched payments as PROCESSED and sets ONLINE as payment method"""
        matched_payments = queryset.filter(state=State.MATCHED).all()

        for payment in matched_payments:
            payment.state = State.PROCESSED
            payment.save()

    @staticmethod
    def check_balance(payments: QuerySet) -> None:
        """For each payment, sets state to MATCHED or MANUEL, depending on the payment agreeing with the open amount."""
        for payment in payments.filter(state__in=[State.NEW, State.MANUAL]).all():
            PaymentProcessor._set_type(payment)
            PaymentProcessor._check_balance(payment)

    @staticmethod
    def _set_type(payment: Payment) -> None:
        if payment.subscription_payments.exists():
            payment.type = Type.SUBSCRIPTION_PAYMENT
            payment.save()

    @staticmethod
    def _check_balance(payment: Payment) -> bool:
        """
        Updates the payment according to currently linked subscriptions.

        Returns true if the payment's amount is equals to the sum of the matched subscriptions.
        """
        if (
            payment.state in [State.NEW, State.MANUAL]
            and payment.type == Type.SUBSCRIPTION_PAYMENT
        ):
            remaining_amount = (
                payment.amount - payment.subscription_payments_amount_sum()
            )

            if remaining_amount.is_zero():
                payment.state = State.MATCHED
                payment.amount_to_reimburse = 0
                payment.save()
                return True
            elif remaining_amount > 0:
                payment.amount_to_reimburse = remaining_amount
                payment.state = State.MANUAL
                payment.save()
                return False
            else:
                payment.state = State.MANUAL
                payment.save()
                return False
