from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsOwnerOrAuthenticatedReadOnly
from relationships.models import Follow
from relationships.serializers import FollowSerializer


class FollowViewSet(mixins.DestroyModelMixin, GenericViewSet):
    """
    팔로우 삭제
    DELETE /api/follows/{follows_id}
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]


class FollowNestedViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    팔로우
    생성, 리스트
    POST, GET /api/users/{user_id}/follows
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id,
                        to_user_id=self.kwargs['user_pk'])

    def filter_queryset(self, queryset):
        if self.request.user.is_authenticated:
            queryset = queryset.filter(owner=self.request.user)
        return super().filter_queryset(queryset)
