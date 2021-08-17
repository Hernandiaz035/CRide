"""Circle serilizers."""

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

# Django REST framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Serializers
from cride.users.serializers.profiles import ProfileModelSerializer

# Utilities
import jwt
from datetime import timedelta

# Models
from cride.users.models import (User, Profile)


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    profile = ProfileModelSerializer(read_only=True)

    class Meta:
        """Meta class."""
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'profile',
            'email',
            'phone_number',
        )


class AccountVerificationSerializer(serializers.Serializer):
    """Account verification serializer."""
    token = serializers.CharField()

    def validate_token(self, data):
        """Check token."""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            raise serializers.ValidationError('Invalid token.')
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Expired signature.')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Unknown Error.')

        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token type.')

        self.context['payload'] = payload

        return data

    def validate(self, data):
        return data

    def save(self):
        """Update user's verified status."""
        payload = self.context['payload']

        user = User.objects.get(username=payload['username'])
        user.is_verified = True
        user.save()


class UserLoginSerializer(serializers.Serializer):
    """Handle the login request data."""
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Check credentials."""
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invlid Credentials.')
        if not user.is_verified:
            raise serializers.ValidationError('The account is not active yet.')
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retieve a token."""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class UserSignupSerializer(serializers.Serializer):
    """User signup serializer.

    Handle sign up data validation and user/profile creation.
    """
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    # Phone number
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Phone number must be entered in the format +99999999999. Up to 15 digits allowed."
    )
    phone_number = serializers.CharField(max_length=17, validators=[phone_regex])

    # Password
    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    def validate(self, data):
        """Verify passwords match."""
        password = data['password']
        password_confirmation = data['password_confirmation']
        if password != password_confirmation:
            raise serializers.ValidationError('Password confirmation does not match!.')
        password_validation.validate_password(password)
        return data

    def create(self, data):
        """Handle user and profile creation."""
        data.pop('password_confirmation')
        user = User.objects.create_user(**data, is_verified=False, is_client=True)
        Profile.objects.create(user=user)
        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        """Send account verification link to given user."""
        verification_token = self.gen_verification_token(user)

        subject = "Welcome @{}! Verify your account to start using Comparte Ride.".format(user.username)
        from_email = 'Comparte Ride <noreply@comparteride.com>'
        content = render_to_string(
            'emails/users/account_verification.html',
            {'token': verification_token, 'user': user}
        )
        msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
        msg.attach_alternative(content, "text/html")
        msg.send()

    def gen_verification_token(self, user):
        """Create the JWT token that the user can use to verify their account."""
        exp_date = timezone.now() + timedelta(days=3)
        payload = {
            'username': user.username,
            'exp': int(exp_date.timestamp()),
            'type': 'email_confirmation'
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
