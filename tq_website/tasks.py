from celery import shared_task
from django.conf import settings
from post_office.mail import send_queued

from groups.services import update_groups
from survey.services import send_course_surveys
from payment.payment_processor import PaymentProcessor
from payment.parser import ISO2022Parser, ZkbCsvParser


@shared_task(
    name="post_office_send_queued_emails",
    ignore_result=True,
    **settings.CELERY_EMAIL_TASK_CONFIG
)
def send_queued_emails() -> None:
    send_queued()


@shared_task(name="payment_parse_zkb_csv_files", ignore_result=True)
def payment_parse_zkb_csv_files() -> None:
    ZkbCsvParser.parse_files_and_save_payments()


@shared_task(name="payment_match", ignore_result=True)
def match_payments() -> None:
    PaymentProcessor().process_payments()


@shared_task(name="update_groups", ignore_result=True)
def task_update_groups() -> None:
    update_groups()


@shared_task(name="send_course_surveys", ignore_result=True)
def task_send_course_surveys() -> None:
    send_course_surveys()