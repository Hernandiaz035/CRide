"""Circle permission classes."""

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from cride.circles.models import Membership

class IsCircleAdmin(BasePermission):
    """Allow access only to circle's admins."""

    def has_object_permission(self, request, view, obj):
        """Verify that the user has a Membership in the object."""

        try:
            Membership.objects.get(
                user=request.user,
                circle=obj,
                is_admin=True,
                is_active=True
            )
        except Membership.DoesNotExist:
            return False
        return True
