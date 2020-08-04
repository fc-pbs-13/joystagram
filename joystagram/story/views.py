from datetime import timedelta
from time import sleep

from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, mixins
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsOwnerOrAuthenticatedReadOnly
from relationships.models import Follow
from story.models import Story, StoryCheck
from story.serializers import StorySerializer, StoryListSerializer
from users.models import User
from users.serializers import SimpleProfileSerializer


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]


    def retrieve(self, request, *args, **kwargs):

        # 캐시 검사
        key = f'{kwargs["pk"]}story'
        instance = cache.get(key)
        if not instance:
            instance = self.get_object()
            cache.set(key, instance, 60)

        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        response = Response(serializer.data)

        # 조회 성공 시 StoryCheck get_or_create
        if (response.status_code == status.HTTP_200_OK) and (request.user.id != response.data['owner']['id']):
            StoryCheck.objects.get_or_create(user=request.user, story_id=response.data.get('id'))
        return response

    def get_serializer_class(self):
        if self.action == 'list':
            return StoryListSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == 'retrieve':
            return super().get_queryset().prefetch_related('story_checks')
        return super().get_queryset()

    def filter_queryset(self, qs):
        """
        자신 or 자신이 팔로우하는 유저의 스토리 중
        등록시간 24시간 이내의 것만 리스트
        """
        qs = super().filter_queryset(qs)
        qs = qs.filter(
            created__gte=timezone.now() - timedelta(days=1),
            created__lte=timezone.now()
        ).filter(
            Q(owner_id__in=Follow.objects.filter(owner=self.request.user).values('to_user_id')) |
            Q(owner=self.request.user)
        ).select_related('owner__profile')

        if self.action == 'retrieve':
            return qs.prefetch_related('story_checks')
        return qs

    def paginate_queryset(self, queryset):
        # is_watched(bool) 주입
        page = super().paginate_queryset(queryset)
        if self.request.user.is_authenticated:
            story_check_qs = StoryCheck.objects.filter(user=self.request.user, story__in=page)
            self.story_check_dict = {
                story_check.story_id: (story_check.id is not None) for story_check in story_check_qs
            }
        return page

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class StoryReadUserViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    자신의 스토리를 본 유저 리스트
    /api/story/{story_id}/users
    """
    queryset = User.objects.all()
    serializer_class = SimpleProfileSerializer
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]

    def list(self, request, *args, **kwargs):
        story_pk = self.kwargs.get('story_pk')
        if story_pk is None:
            raise ValidationError('story_pk is required')
        story = get_object_or_404(Story, id=story_pk)
        if story.owner_id != request.user.id:
            raise PermissionDenied()
        return super().list(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset). \
            filter(storycheck__story=self.kwargs.get('story_pk')). \
            select_related('profile')
