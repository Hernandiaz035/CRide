"""Circle Views."""

# Django REST framework
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# Models
from cride.circles.models import Circle

# Serializers
from cride.circles.serializers import CirlcleModelSerializer


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set."""

    serializer_class = CirlcleModelSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Circle.objects.all()
        if self.action == 'list':
            return queryset.filter(public=True)
        return queryset
