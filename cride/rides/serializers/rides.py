"""Rides Serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.rides.models import Ride
from cride.circles.models import Membership
from cride.users.models import User

# Serializers
from cride.users.serializers import UserModelSerializer

# Utilities
from datetime import timedelta
from django.utils import timezone


class RideModelSerializer(serializers.ModelSerializer):
    """Ride Model Serializer."""

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField(read_only=True)

    passengers = UserModelSerializer(read_only=True, many=True)

    available_seats = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        """Meta class."""
        model = Ride
        fields = '__all__'
        read_only_fields = [
            'offered_by',
            'offered_in',
            'rating',
        ]

    def update(self, instance, validated_data):
        """Allow updates only before departure time."""
        now = timezone.now()
        if instance.departure_date >= now:
            serializers.ValidationError('Ongoing rides cannot be modified.')
        return super(RideModelSerializer, self).update(instance, validated_data)

class CreateRideSerializer(serializers.ModelSerializer):
    """Create Ride serializer."""

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_seats = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        """Meta class."""
        model = Ride
        exclude = [
            'offered_in',
            'passengers',
            'rating',
            'is_active',
        ]
    def validate_departure_date(self, data):
        """Verify date is not in the past."""
        min_date = timezone.now() + timedelta(minutes=10)
        if data < min_date:
            raise serializers.ValidationError(
                'Departure time must be at least 20 minutes in the future. '
            )
        return data

    def validate(self, data):
        """Validate.

        Verify that the person who offers the ride is member
        and also the same user making the request.
        """
        user = data['offered_by']
        circle = self.context['circle']
        try:
            membership = Membership.objects.get(user=user, circle=circle, is_active=True)
            self.context['membership'] = membership
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle.')

        if data['arrival_date'] < data['departure_date']:
            raise serializers.ValidationError('Arrival time has to happen after the departure.')

        return data

    def create(self, validated_data):
        """Create Ride and Update Stats."""
        circle = self.context['circle']
        ride = Ride.objects.create(**validated_data, offered_in=circle)

        # Circle
        circle.rides_offered += 1
        circle.save()

        # Membership
        membership = self.context['membership']
        membership.rides_offered += 1
        membership.save()

        # Profile
        profile = validated_data['offered_by'].profile
        profile.rides_offered += 1
        profile.save()

        return ride


class JoinRideSerializer(serializers.ModelSerializer):
    """Join Ride Serializer."""

    passenger = serializers.CharField()

    class Meta:
        """Meta class."""
        model = Ride
        fields = ['passenger']

    def validate_passenger(self, data):
        """Validate Passenger."""
        try:
            user = User.objects.get(username=data)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exists.')

        circle = self.context['circle']
        try:
            self.context['member'] = Membership.objects.get(
                circle=circle,
                user=user,
                is_active=True
            )
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User does not belong to the circle.')

        self.context['user'] = user

        return data

    def validate(self, data):
        """Verify ride allow new passengers."""
        ride = self.context['ride']
        if ride.departure_date < timezone.now():
            raise serializers.ValidationError('Passenger cannot join this ride now.')

        if ride.available_seats < 1:
            raise serializers.ValidationError('There is no room in this ride.')

        if ride.passengers.filter(username=data['passenger']).exists():
            raise serializers.ValidationError('User is already joined in the ride.')

        if ride.offered_by == self.context['user']:
            raise serializers.ValidationError('The ride creator cannot be a passenger.')

        return data

    def update(self, ride, _):
        """Add passenger to ride and update Stats."""
        user = self.context['user']

        # Ride
        ride.passengers.add(user)
        ride.available_seats -= 1
        ride.save()

        # Profile
        profile = user.profile
        profile.rides_taken += 1
        profile.save()

        # Membership
        member = self.context['member']
        member.rides_taken += 1
        member.save()

        # Circle
        circle = self.context['circle']
        circle.rides_taken += 1
        circle.save()

        return ride


class EndRideSerializer(serializers.ModelSerializer):
    """Finish Ride Serializer."""

    is_active = serializers.BooleanField()
    current_time = serializers.DateTimeField()

    class Meta:
        """Meta Class."""
        model = Ride
        fields = ['is_active', 'current_time']

    def validate_current_time(self, data):
        """Verify ride has started."""
        if self.context['ride'].departure_date >= data:
            raise serializers.ValidationError("Ride Hasn't started yet.")
        return data
