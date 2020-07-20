from django.contrib.auth import logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, mixins
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsUserSelf
from relationships.models import Follow
from relationships.serializers import FollowSerializer, FollowingSerializer, FollowerSerializer
from users.models import User, Profile
from users.serializers import UserSerializer, LoginSerializer, UserPasswordSerializer, SimpleProfileSerializer


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserSelf]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'retrieve':
            qs = qs.select_related('profile')

        if self.action == 'followers':
            qs = qs.filter(
                id__in=Follow.objects.filter(to_user_id=self.kwargs['pk']).values('from_user_id')
            )
        if self.action == 'followings':
            qs = qs.filter(
                id__in=Follow.objects.filter(from_user_id=self.kwargs['pk']).values('to_user_id')
            )
            # return Follow.objects.filter(from_user=self.kwargs['pk'])

        # User 조회, 리스트 시 Profile select_related
        # if self.action in ('retrieve', 'followings', 'followers'):
        #     qs = qs.select_related('profile')
        return qs

    def get_permissions(self):
        if self.action in ('login', 'create'):
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'update_password':
            return UserPasswordSerializer
        if self.action == 'followers':
            return SimpleProfileSerializer
        if self.action == 'followings':
            return SimpleProfileSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'])
    def login(self, request):
        """로그인 시리얼라이저로 valid 후 토큰 생성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    @action(detail=False, methods=['delete'])
    def logout(self, request):
        """토큰 삭제, 토큰 없다면 400 리턴"""
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response({"detail": "Not authorized User."},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Successfully logged out."},
                        status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """유저 삭제
        TODO safe delete 변경예정(is_active)"""
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def update_password(self, request, *args, **kwargs):
        """비밀번호 변경"""
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True)
    def followers(self, request, *args, **kwargs):
        """
        TODO nested url ViewSet 으로 분리 /api/users/{user_id}/followers
        유저를 팔로우하는 유저 리스트
        followers -> user
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def followings(self, request, *args, **kwargs):
        """
        TODO nested url ViewSet 으로 분리 /api/users/{user_id}/followings
        유저가 팔로잉하는 유저 리스트
        user -> followings
        """
        return super().list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """기본 list 엔드포인트는 차단"""
        response = {'message': 'GET method is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)
