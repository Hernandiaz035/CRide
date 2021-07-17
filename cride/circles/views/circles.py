"""Circle Views."""

# Django REST framework
from rest_framework import viewsets

# Models
from cride.circles.models import Circle

# Serializers
from cride.circles.serializers import CirlcleModelSerializer


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set."""

    queryset = Circle.objects.all()
    serializer_class = CirlcleModelSerializer
