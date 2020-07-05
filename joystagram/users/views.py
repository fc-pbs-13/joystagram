from django.contrib.auth import logout as django_logout, authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from users.models import User, UserProfile
from users.serializers import UserSerializer, UserAuthTokenSerializer, UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'login':
            return UserAuthTokenSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    @action(detail=False, methods=['delete'])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response({"detail": "Not authorized User."},
                            status=status.HTTP_400_BAD_REQUEST)
        django_logout(request)
        return Response({"detail": "Successfully logged out."},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def deactivate(self, request, *args, **kwargs):
        # get_object_or_404() 활용
        # https://www.django-rest-framework.org/api-guide/generic-views/#get_objectself
        user = get_object_or_404(User.objects.all(), id=request.user.id)
        user.delete()
        return Response({"detail": "Account successfully deleted."},
                        status=status.HTTP_204_NO_CONTENT)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
