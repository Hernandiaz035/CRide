"""Rides Permissions."""

# Django REST Framework
from rest_framework.permissions import BasePermission


class IsRideOwner(BasePermission):
    """Verify requesting user is the ride creator."""
    def has_object_permission(self, request, view, obj):
        """Verify requesting user is the ride creator."""
        return obj.offered_by == request.user
