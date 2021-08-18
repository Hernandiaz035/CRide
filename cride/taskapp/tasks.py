"""Celery Tasks."""

# Django
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives

# Models
from cride.users.models import User
from cride.rides.models import Ride

# Celery
from celery.decorators import task, periodic_task

# Utilities
import jwt
from datetime import timedelta
from time import sleep


@task(name='send_confirmation_email', max_retries=3)
def send_confirmation_email(user_pk):
    """Send account verification link to given user."""
    for i in range(10):
        sleep(1)
        print(f"Sleeping.......{i+1}......")
    user = User.objects.get(pk=user_pk)
    verification_token = gen_verification_token(user_pk=user.pk)

    subject = "Welcome @{}! Verify your account to start using Comparte Ride.".format(user.username)
    from_email = 'Comparte Ride <noreply@comparteride.com>'
    content = render_to_string(
        'emails/users/account_verification.html',
        {'token': verification_token, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


def gen_verification_token(user_pk):
    """Create the JWT token that the user can use to verify their account."""
    user = User.objects.get(pk=user_pk)
    exp_date = timezone.now() + timedelta(days=3)
    payload = {
        'username': user.username,
        'exp': int(exp_date.timestamp()),
        'type': 'email_confirmation'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


@periodic_task(name='disable_finished_rides', run_every=timedelta(seconds=10))
def disable_finished_rides():
    """Disable Finished Rides."""
    now = timezone.now()
    offset = now + timedelta(seconds=5)

    # Update rides that have already finish
    rides = Ride.objects.filter(
        is_active=True,
        arrival_date__gte=now,
        arrival_date__lte=offset
    )
    rides.update(is_active=False)
