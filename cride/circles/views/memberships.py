"""Circle's memberships views."""

# Django REST Framework
from rest_framework import mixins, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember, IsSelfMember

# Serializer
from cride.circles.serializers import MembershipModelSerializer

# Model
from cride.circles.models import Circle, Membership, Invitation


class MembershipViewset(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
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
        if self.action == 'invitations':
            permissions.append(IsSelfMember)
        return [p() for p in permissions]

    def get_queryset(self):
        """Returns  circle's members."""
        return Membership.objects.filter(
            circle=self.circle,
            is_active=True
        )

    def get_object(self):
        """Return circle member by providing the user's username."""
        return get_object_or_404(
            Membership,
            user__username=self.kwargs['pk'],
            circle=self.circle,
            is_active=True
        )

    def perform_destroy(self, instance):
        """Set the Membership relation inactive."""
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['get'])
    def invitations(self, request, *args, **kwargs):
        """Retrieve a member's invitations breakdown.

        Will return a list containing all the members tha have
        used its invitations and another list containing the
        invitations tha haven't been used.
        """

        invited_members = Membership.objects.filter(
            circle=self.circle,
            invited_by=request.user,
            is_active=True
        )

        invitations = Invitation.objects.filter(
            circle=self.circle,
            issued_by=request.user,
            used=False
        ).values_list('code', flat=True)
        invitations = list(invitations)

        diff = self.get_object().remaining_invitations - len(invitations)

        for i in range(diff):
            invitations.append(
                Invitation.objects.create(
                    issued_by=request.user,
                    circle=self.circle
                ).code
            )

        data = {
            "used_invitations": MembershipModelSerializer(invited_members, many=True).data,
            "unsued_invitations": invitations
        }

        return Response(data, status=status.HTTP_200_OK)
