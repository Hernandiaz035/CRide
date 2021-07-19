"""Circle serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.circles.models import Circle


class CirlcleModelSerializer(serializers.ModelSerializer):
    """Circle Serializer."""

    members = serializers.StringRelatedField(many=True, read_only=True)

    members_limit = serializers.IntegerField(
        required=False,
        min_value=10,
        max_value=32000
    )
    is_limited = serializers.BooleanField(default=False)
    class Meta:
        """Meta class."""
        model = Circle
        fields = (
            'slug_name',
            'name',
            'about',
            'picture',
            'rides_taken',
            'rides_offered',
            'verified',
            'public',
            'members',
            'is_limited',
            'members_limit',
        )

        read_only_fields = (
            'public',
            'verified',
            'rides_offered',
            'rides_taken',
        )

    def validate(self, data):
        """Ensure both members_limit and is_limited are present."""
        members_limit = data.get('members_limit', 0)
        is_limited = data.get('is_limited', False)

        if not members_limit and is_limited:
            raise serializers.ValidationError(
                'If circle is limited a members limit must be provided.'
            )
        if members_limit and not is_limited:
            raise serializers.ValidationError(
                'If circle is not limited a members limit must not be provided.'
            )

        return data
