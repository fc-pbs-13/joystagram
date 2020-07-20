from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, status

from core.permissions import IsOwnerOrReadOnly
from relationships.models import Follow
from story.models import Story, StoryCheck
from story.serializers import StorySerializer, StoryListSerializer


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return StoryListSerializer
        return super().get_serializer_class()

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)
        self.story_check_dict = {}
        if self.request.user.is_authenticated:
            check_qs = StoryCheck.objects
            user = self.request.user
            self.story_check_dict = {story.id: check_qs.filter(story_id=story.id, user=user).exists() for story in page}
        return page

    def filter_queryset(self, queryset):
        """자신이 팔로우하는 유저의 스토리 중 등록시간 24시간 이내의 것만 필터링"""
        qs = super().filter_queryset(queryset)

        # TODO 등록시간 24시간 이내의 스토리만
        yesterday = timezone.now() - timedelta(days=1)
        qs = Story.objects.filter(created__gte=yesterday,
                                  created__lte=timezone.now())
        # 자신이 팔로우한 유저의 것만
        return qs.filter(owner_id__in=Follow.objects.filter(from_user=self.request.user).values('to_user_id'))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        # 스토리 조회 성공 시 StoryCheck get_or_create
        if response.status_code == status.HTTP_200_OK:
            StoryCheck.objects.get_or_create(user=request.user, story_id=response.data.get('id'))
        return response
