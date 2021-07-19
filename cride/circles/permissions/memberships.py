"""Membership Permissions."""

# Django REST Framework
from rest_framework import permissions

# Models
from cride.circles.models import Membership


class IsActiveCircleMember(permissions.BasePermission):
    """Allow access only to circle members.

    Expect that views implementing this permissions
    has 'circle' attribute assigned.
    """

    def has_permission(self, request, view):
        """Verify user is an active member of a circle."""
        try:
            Membership.objects.filter(
                circle=view.circle,
                user=request.user,
                is_active=True
            )
        except Membership.DoesNotExist:
            return False
        return True
