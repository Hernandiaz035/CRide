"""Rides Views."""


# Django REST Framework
from rest_framework import mixins, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsActiveCircleMember
from cride.rides.permissions import IsRideOwner

# Serializers
from cride.rides.serializers import (
    RideModelSerializer,
    CreateRideSerializer,
    JoinRideSerializer,
    EndRideSerializer,
)

# Filtes
from rest_framework.filters import SearchFilter, OrderingFilter

# Models
from cride.circles.models import Circle
from cride.rides.models import Ride

# Utilities
from datetime import timedelta
from django.utils import timezone


class RideViewset(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """Ride View set."""

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['departure_location', 'arrival_location']
    ordering = ['departure_date', 'arrival_date', '-available_seats']
    ordering_fields = ['departure_date', 'arrival_date', 'available_seats']

    def dispatch(self, request, *args, **kwargs):
        """Verifies that the circle exists."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(RideViewset, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return active circle's Rides."""
        if self.action == 'finish':
            return self.circle.ride_set.all()
        offset = timezone.now() + timedelta(minutes=10)
        return self.circle.ride_set.filter(
            departure_date__gte=offset,
            available_seats__gte=1,
            is_active=True
        )

    def get_permissions(self):
        """Return permissions based on the performing acton."""
        permissions = [IsAuthenticated, IsActiveCircleMember]

        if self.action in ['update', 'partial_update', 'finish']:
            permissions.append(IsRideOwner)

        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on actions."""
        if self.action == 'create':
            return CreateRideSerializer
        if self.action == 'join':
            return JoinRideSerializer
        if self.action == 'finish':
            return EndRideSerializer
        return RideModelSerializer

    def get_serializer_context(self):
        """Return serializer context based on actions."""
        context = super(RideViewset, self).get_serializer_context()
        context['circle'] = self.circle
        if self.action in ['join', 'finish']:
            context['ride'] = self.get_object()
        return context

    @action(detail=True, methods=['POST'])
    def join(self, request, *args, **kwargs):
        """Add requestiing user to ride."""
        ride = self.get_object()
        serializer = self.get_serializer(
            ride,
            data={'passenger': request.user.username},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()

        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def finish(self, request, *args, **kwargs):
        """Finish Ride by its owner."""
        ride = self.get_object()
        serializer = self.get_serializer(
            ride,
            data={'is_active': False, 'current_time': timezone.now()},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)
