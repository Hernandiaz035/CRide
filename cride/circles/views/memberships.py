"""Circle's memberships views."""

# Django REST Framework
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember

# Serializer
from cride.circles.serializers import MembershipModelSerializer

# Model
from cride.circles.models import Circle, Membership


class MembershipViewset(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Circle membership view set."""

    serializer_class = MembershipModelSerializer

    def dispatch(self, request, *args, **kwargs):
        """Verifies that the circle exists."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(MembershipViewset, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permissions based on the performed actions."""
        permissions = [IsAuthenticated, IsActiveCircleMember]
        return [p() for p in permissions]

    def get_queryset(self):
        """Returns  circle's members."""
        return Membership.objects.filter(
            circle=self.circle,
            is_active=True
        )
