"""Circle serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.circles.models import Circle


class CirlcleModelSerializer(serializers.ModelSerializer):
    """Circle Serializer."""

    class Meta:
        """Meta class."""
        model = Circle
        fields = '__all__'
