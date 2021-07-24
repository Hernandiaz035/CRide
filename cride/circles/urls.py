"""Circles URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from cride.circles.views import circles as circle_views
from cride.circles.views import memberships as membership_views

router = DefaultRouter()
router.register(r'circles', circle_views.CircleViewSet, basename='circle')
router.register(
    r'circles/(?P<slug_name>[\w-]+)/members',
    membership_views.MembershipViewset,
    basename='membership'
)

urlpatterns = [
    path('', include(router.urls))
]
