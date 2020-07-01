from django.contrib.auth import logout as django_logout, login, authenticate
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, settings, mixins
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.models import User
from users.serializers import UserSerializer, UserLoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'login':
            return UserLoginSerializer
        return super().get_serializer_class()

    @action(methods=('post',), detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        # user = serializer.validated_data['user']
        # token, created = Token.objects.get_or_create(user=user)
        # return Response({'token': token.key})
        print(serializer.data)
        return Response(serializer.data)

    # @action(detail=False, methods=['post'])
    # def login(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     email = serializer.validated_data['email']
    #     password = serializer.validated_data['password']
    #     user = authenticate(email=email, password=password)
    #     if user is not None:
    #         token, created = Token.objects.get_or_create(user=user)
    #         # 필요한지 확인
    #         login(request, user)
    #         return Response({'token': token.key, 'email': user.email}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'detail': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response({"detail": "Not authorized User."},
                            status=status.HTTP_400_BAD_REQUEST)
        # 필요한지 확인
        if getattr(settings, 'REST_SESSION_LOGIN', True):
            django_logout(request)
            return Response({"detail": "Successfully logged out."},
                            status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def deactivate(self, request, *args, **kwargs):
        # get_object_or_404() 활용
        # https://www.django-rest-framework.org/api-guide/generic-views/#get_objectself
        # user = get_object_or_404(User.objects.all(), id=request.user.id)

        try:
            # request.user.delete()
            # 필요한지 확인
            user = self.get_object()
            user.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response({"detail": "Not authorized User."},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Account successfully deleted."},
                        status=status.HTTP_204_NO_CONTENT)
