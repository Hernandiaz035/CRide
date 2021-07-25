"""Rides Views."""


# Django REST Framework
from rest_framework import mixins, viewsets, status
from rest_framework.generics import get_object_or_404

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsActiveCircleMember
from cride.rides.permissions import IsRideOwner

# Serializers
from cride.rides.serializers import (
    RideModelSerializer,
    CreateRideSerializer
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
        offset = timezone.now() + timedelta(minutes=10)
        return self.circle.ride_set.filter(
            departure_date__gte=offset,
            available_seats__gte=1,
            is_active=True
        )

    def get_permissions(self):
        """Return permissions based on the performing acton."""
        permissions = [IsAuthenticated, IsActiveCircleMember]

        if self.action in ['update', 'partial_update']:
            permissions.append(IsRideOwner)

        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on actions."""
        if self.action == 'create':
            return CreateRideSerializer
        return RideModelSerializer

    def get_serializer_context(self):
        """Add circle to serializer context."""
        context = super(RideViewset, self).get_serializer_context()
        context['circle'] = self.circle
        return context
