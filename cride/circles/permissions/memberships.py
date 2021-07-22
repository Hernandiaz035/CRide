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
            Membership.objects.get(
                circle=view.circle,
                user=request.user,
                is_active=True
            )
        except Membership.DoesNotExist:
            return False
        return True

class IsSelfMember(permissions.BasePermission):
    """Allow access only to the membership owner."""

    def has_permission(self, request, view):
        """Let object permission grant access."""
        return self.has_object_permission(request, view, view.get_object())

    def has_object_permission(self, request, view, obj):
        """Verify that the user is the onwer of the membership."""
        return obj.user == request.user
