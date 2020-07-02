from django.conf import settings
from django.contrib.auth import logout as django_logout, login, authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework import viewsets, settings
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            # 필요한지 확인
            login(request, user)
            return Response({'token': token.key, 'email': user.email}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False)
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
