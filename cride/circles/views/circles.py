"""Circle Views."""

# Django REST framework
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed

# Models
from cride.circles.models import Circle, Membership

# Serializers
from cride.circles.serializers import CircleModelSerializer

# Permissions
from cride.circles.permissions import IsCircleAdmin


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set."""

    serializer_class = CircleModelSerializer

    lookup_field = 'slug_name'

    def get_queryset(self):
        queryset = Circle.objects.all()
        if self.action == 'list':
            return queryset.filter(public=True)
        return queryset

    def get_permissions(self):
        """Assign permissions based on actions."""
        permissions = [IsAuthenticated,]
        if self.action in ['update', 'partial_update']:
            permissions.append(IsCircleAdmin)
        elif self.action == 'destroy':
            raise MethodNotAllowed('DELETE')

        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        """Assign Circle's Admin and default details."""
        circle = serializer.save()
        user = self.request.user
        profile = user.profile

        Membership.objects.create(
            user=user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10,
        )
