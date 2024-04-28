from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

import datetime

from events.models import Event, EventCategory
from events.models.event_registration import EventRegistration


def detail(request, event_id):
    template_name = "events/event_detail.html"
    event = get_object_or_404(Event, pk=event_id)
    context = {"event": event, "user_registered": event.is_registered(request.user)}
    return render(request, template_name, context)


def category_detail(request: HttpRequest, category_id: int) -> HttpResponse:
    template_name = "events/category_detail.html"
    category = get_object_or_404(EventCategory, pk=category_id)
    context = {
        "events": Event.displayed_events.future().filter(category=category).all(),
        "use_cards": False,
        "title": category.name,
        "text": category.description,
        "image": category.image,
        "show_when_no_events": True,
    }
    return render(request, template_name, context)


def archive(request: HttpRequest, year: int | None = None):
    template_name = "events/archive.html"
    today = timezone.now()
    if year is None:
        year = today.year

    context = {
        "year": year,
        "events": Event.objects.filter(date__year=year, date__lt=today)
        .all()
        .order_by("date"),
    }
    return render(request, template_name, context)


@login_required
def register(request, event_id):
    user_id = request.user.id
    try:
        registration = EventRegistration(user_id=user_id, event_id=event_id)
        registration.save()
    except IntegrityError:
        pass  # Already registered
    return redirect("events:registration_confirmation", event_id)


@login_required
def unregister(request, event_id):
    user_id = request.user.id
    try:
        registration = EventRegistration.objects.get(user_id=user_id, event_id=event_id)
        registration.delete()
    except EventRegistration.DoesNotExist:
        pass  # Already unregistered
    return redirect("events:registration_removed", event_id)


def registration_confirmation(request, event_id):
    template_name = "events/event_detail.html"
    event = get_object_or_404(Event, pk=event_id)
    context = {
        "event": event,
        "user_registered": event.is_registered(request.user),
        "is_registration_confirmation": True,
    }
    return render(request, template_name, context)


def registration_removed(request, event_id):
    template_name = "events/event_detail.html"
    event = get_object_or_404(Event, pk=event_id)
    context = {
        "event": event,
        "user_registered": event.is_registered(request.user),
        "is_registration_removed": True,
    }
    return render(request, template_name, context)
