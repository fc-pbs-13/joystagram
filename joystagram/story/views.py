from rest_framework import viewsets, status

from core.permissions import IsOwnerOrReadOnly
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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        # TODO 조회 성공 시 StoryCheck 생성
        if response.status_code == status.HTTP_200_OK:
            StoryCheck.objects.create(user=request.user, story_id=response.data.get('id'))
        return response
