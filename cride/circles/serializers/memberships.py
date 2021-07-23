"""Circle Members Serializer."""

# Django
from django.utils import timezone

# Django REST Framework
from rest_framework import serializers

# Serializers
from cride.users.serializers import UserModelSerializer

# Models
from cride.circles.models import Membership, Invitation


class MembershipModelSerializer(serializers.ModelSerializer):
    """Member Model serializer."""

    user = UserModelSerializer(read_only=True)
    invited_by = serializers.StringRelatedField()
    joined_at = serializers.DateTimeField(source='created', read_only=True)

    class Meta:
        """Meta class."""
        model = Membership
        fields = (
            'user',
            'is_admin',
            'is_active',
            'used_invitations',
            'remaining_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered',
            'joined_at',
        )
        read_only_fields = (
            'user',
            'used_invitations',
            'remaining_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered',
        )


class AddMemberSerializer(serializers.Serializer):
    """Add Member serializer.

    Haddle the addition of a new member to a circle.
    Circle object must be provided in the context.
    """

    invitation_code = serializers.CharField(min_length=8)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_user(self, data):
        """Verify user is not already a member."""
        circle = self.context['circle']
        user = data
        q = Membership.objects.filter(circle=circle, user=user)
        if q.exists():
            raise serializers.ValidationError('The user is already a member of this circle.')
        return data

    def validate_invitation_code(self, data):
        """Verify code exists and it is related to the circle."""
        try:
            invitation = Invitation.objects.get(
                code=data,
                circle=self.context['circle'],
                used=False
            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError('Invalid invitation code.')

        self.context['invitation'] = invitation
        return data

    def validate(self, data):
        """Verify the members limit of the circle has not been reached."""
        circle = self.context['circle']
        if circle.is_limited and circle.members.count() >= circle.members_limit:
            raise serializers.ValidationError('Circle has reached its members limit.')

        return super().validate(data)

    def create(self, validated_data):
        """Create circle member."""
        circle = self.context['circle']
        invitation = self.context['invitation']
        user = validated_data['user']

        now = timezone.now()

        # create member
        member = Membership.objects.create(
            user=user,
            profile=user.profile,
            circle=circle,
            invited_by=invitation.issued_by,
        )

        # update invitation
        invitation.used_by = user
        invitation.used = True
        invitation.used_at = now
        invitation.save()

        # update issuer stats
        issuer = Membership.objects.get(
            circle=circle,
            user=invitation.issued_by
        )
        issuer.used_invitations += 1
        issuer.remaining_invitations -= 1
        issuer.save()

        return member
