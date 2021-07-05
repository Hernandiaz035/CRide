"""Circle serilizers."""

# Django REST framework
from rest_framework import serializers

# Models
from cride.circles.models import Circle


class CircleSerializer(serializers.Serializer):
    """Circle Serializer."""
    name = serializers.CharField()
    slug_name = serializers.SlugField()

    rides_taken = serializers.IntegerField()
    rides_offered = serializers.IntegerField()

    members_limit = serializers.IntegerField()


class CreateCirlceSerializer(serializers.Serializer):
    """Create Circle serializar."""
    name = serializers.CharField(max_length=140)
    slug_name = serializers.SlugField(max_length=40)

    about = serializers.CharField(
        max_length=255,
        required=False
    )

    def create(self, data):
        """Create circle."""
        return Circle.objects.create(**data)
