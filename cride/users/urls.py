"""Users URLs."""

# Django
from django.urls import include, path

# Django REST FrameWork
from rest_framework.routers import DefaultRouter

# Views
from cride.users.views import users as user_views

routers = DefaultRouter()
routers.register(r'users', user_views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(routers.urls))
]
