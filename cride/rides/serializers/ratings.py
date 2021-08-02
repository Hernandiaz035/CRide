"""Rating Serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.rides.models import Rating

# Utilities
from django.db.models import Avg


class RateRideSerializer(serializers.ModelSerializer):
    """Rate Ride Serializer."""

    class Meta:
        """Meta class."""
        model = Rating

        fields = [
            'ride',
            'circle',
            'rating_user',
            'rated_user',
            'rating',
            'comments'
        ]

    def validate_rating_user(self, data):
        """Verify the requesting user is a passenger in the ride."""
        if not self.context['ride'].passengers.filter(username=data.username).exists():
            raise serializers.ValidationError('User is not a passenger of the ride.')
        return data

    def validate_rating(self, data):
        """Verify the rating is in the admited range"""
        if data < 1 or data > 5:
            raise serializers.ValidationError('The rating is not valid.')
        return data

    def validate(self, data):
        """Verify the rate is not duplicated and it has finished."""
        q = Rating.objects.filter(
            circle=data['circle'],
            ride=data['ride'],
            rating_user=data['rating_user']
        )
        if q.exists():
            raise serializers.ValidationError('The ride has already been rated.')
        return data

    def create(self, data):
        """Create Rating and update rating in the ride."""
        ride = data['ride']
        rating = Rating.objects.create(**data)

        # Ride
        ride.rating = round(
            Rating.objects.filter(
                circle=ride.offered_in,
                ride=ride
            ).aggregate(Avg('rating'))['rating__avg'],
            1
        )
        ride.save()

        # Rated User
        rated_user = data['rated_user']
        rated_user.profile.reputation = round(
            Rating.objects.filter(
                rated_user=rated_user
            ).aggregate(Avg('rating'))['rating__avg'],
            1
        )
        rated_user.profile.save()

        return rating
