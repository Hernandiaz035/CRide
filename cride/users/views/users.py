"""Users views."""

# Django REST framework
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from cride.users.permissions import IsAccountOwner

# Serializers
from cride.users.serializers import (
    UserLoginSerializer,
    UserModelSerializer,
    UserSignupSerializer,
    AccountVerificationSerializer,
)
from cride.circles.serializers.circles import CirlcleModelSerializer

# Models
from cride.users.models import User
from cride.circles.models import Circle


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """User view set.

    Handle signup, login and account verification.
    """

    queryset = User.objects.filter(is_client=True, is_verified=True)
    serializer_class = UserModelSerializer
    lookup_field = 'username'

    def get_permissions(self):
        """Assign permissions based on actions."""
        if self.action in ['signup', 'verify', 'login']:
            permissions = [AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permissions = [IsAuthenticated, IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """User Signup."""
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login."""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token,
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Account verification."""
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'Account Verified!.'}
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        response = super(UserViewSet, self).retrieve(request, *args, **kwargs)
        circles = Circle.objects.filter(
             members=request.user,
             membership__is_active=True
        )
        data = {
            'user': response.data,
            'circles': CirlcleModelSerializer(circles, many=True, read_only=True).data
        }
        response.data = data
        return response
