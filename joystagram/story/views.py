from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status, mixins
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
        """스토리 조회 성공 시 StoryCheck get_or_create"""
        response = super().retrieve(request, *args, **kwargs)

        if (response.status_code == status.HTTP_200_OK) and (request.user.id != response.data['owner']['id']):
            StoryCheck.objects.get_or_create(user=request.user, story_id=response.data.get('id'))
        return response

    def get_serializer_class(self):
        if self.action == 'list':
            return StoryListSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        """자신 or 자신이 팔로우하는 유저의 스토리 중
        등록시간 24시간 이내의 것만 리스트"""

        # 등록시간 24시간 이내
        yesterday = timezone.now() - timedelta(days=1)
        queryset = Story.objects.filter(created__gte=yesterday,
                                        created__lte=timezone.now())
        # owner가 자신 or 팔로잉 유저
        queryset = queryset.filter(
            Q(owner_id__in=Follow.objects.filter(from_user=self.request.user).values('to_user_id')) |
            Q(owner=self.request.user)
        ).select_related('owner__profile')
        return super().filter_queryset(queryset)

    def paginate_queryset(self, queryset):
        # is_watched 주입
        page = super().paginate_queryset(queryset)
        if self.request.user.is_authenticated:
            story_check_qs = StoryCheck.objects.filter(user=self.request.user, story__in=page)
            self.story_check_dict = {story_check.story_id: (story_check.id is not None)
                                     for story_check in story_check_qs}
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
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]  # TODO 내 스토리인지 검사

    def get_queryset(self):
        return super().get_queryset().filter(storycheck__story=self.kwargs.get('story_pk'))
