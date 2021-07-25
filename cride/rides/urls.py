"""Rides URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from cride.rides.views import rides as ride_views

router = DefaultRouter()
router.register(
    r'circles/(?P<slug_name>[\w-]+)/rides',
    ride_views.RideViewset,
    basename='ride'
)

urlpatterns = [
    path('', include(router.urls))
]
