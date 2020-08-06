import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsUserSelf
from relationships.models import Follow
from relationships.serializers import UserListSerializer
from story.models import StoryCheck, Story
from users.models import User
from users.serializers import UserSerializer, LoginSerializer, UserPasswordSerializer



class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsUserSelf]
    permission_classes = []
    authentication_classes = []  # todo

    def filter_queryset(self, qs):
        User.objects.prefetch_related('to')
        if self.action == 'retrieve':
            return qs.select_related('profile').prefetch_related('posts', 'followers__owner', 'followings__to_user')
            # return super().filter_queryset(qs).\
            #     select_related('profile').prefetch_related('posts', 'followers__owner', 'followings__to_user_id')
        if self.action == 'followers':
            qs = qs.filter(
                id__in=Follow.objects.filter(to_user_id=self.kwargs['pk']).values('owner_id')
            ).select_related('profile')
        if self.action == 'followings':
            qs = qs.filter(
                id__in=Follow.objects.filter(owner_id=self.kwargs['pk']).values('to_user_id')
            ).select_related('profile')
        if self.action == 'list':
            nickname = self.request.query_params.get('nickname')
            if not nickname:
                raise ParseError('query parameter required: nickname not supplied')
            qs = qs.filter(profile__nickname__icontains=nickname).select_related('profile')

        return super().filter_queryset(qs)

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)

        # like_id 주입
        if self.request.user.is_authenticated:
            if self.action in ('list', 'followers', 'followings'):
                follow_list = Follow.objects.filter(owner=self.request.user)
                self.follow_id_dict = {follow.to_user_id: follow.id for follow in follow_list}
        return page

    def get_permissions(self):
        if self.action in ('login', 'create'):
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'update_password':
            return UserPasswordSerializer
        if self.action in ('list', 'followers', 'followings'):
            return UserListSerializer
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
        """토큰 삭제"""
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        return Response({"detail": "Successfully logged out."},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def update_password(self, request, *args, **kwargs):
        """비밀번호 변경"""
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True)
    def followers(self, request, *args, **kwargs):
        """
        유저를 팔로우하는 유저 리스트
        followers -> user
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def followings(self, request, *args, **kwargs):
        """
        유저가 팔로잉하는 유저 리스트
        user -> followings
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False)
    def locust_test(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.info('인포메이셔언')
        logger.warning('경고경고경고')
        logger.error('에러...')
        logger.debug('디버깅!')
        return Response()

        # qs.filter(
        #
        # ).select_related('profile')

        # users_qs = User.objects. \
        #     filter(story__created__gte=yesterday, story__created__lte=now). \
        #     filter(
        #     Q(id__in=Follow.objects.filter(owner_id=self.kwargs['pk']).values('to_user_id')) |
        #     Q(id=request.user.id)
        # ).prefetch_related('storycheck_set')

        # Story.objects.values('owner_id').\
        #     filter(owner__in=Follow.objects.filter(owner_id=self.kwargs['pk']).values('to_user_id')).\
        #     filter(created__gte=yesterday, created__lte=now)

        # StoryCheck.objects.filter(story__owner__in=users_qs)
