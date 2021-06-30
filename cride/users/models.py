"""Users Model."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import CharField
from django.core.validators import RegexValidator

# Utilities
from cride.utils.models import CRideModel

class User(CRideModel, AbstractUser):
    """User model.

    Exteds from  django's AbstractUser, change the username field to email
    and add some extrafeatures.
    """
    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with this email already exists.'
        }
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format +99999999999. Up to 15 digits allowed."
    )

    phone_number=models.CharField(validators=[phone_regex], max_length=17, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_client = models.BooleanField(
        'client',
        default=True,
        help_text=(
            'Help esaily distinguish and perfom queries.'
            'Clients are the main type of user.'
        )
    )

    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='Set to true when the user has verified his email.'
    )

    def __str__(self):
        """Return username"""
        return self.username

    def get_short_name(self):
        """Return username"""
        return self.username


