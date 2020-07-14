from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from core.paginations import IDPagination
from core.permissions import IsOwnerOrReadOnly
from posts.models import Post
from posts.serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    게시글 생성, 리스트, 수정, 삭제
    POST, GET
    /api/posts
    UPDATE, DELETE
    /api/posts/{post_id}
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def filter_queryset(self, queryset):
        if self.action == 'feed':
            queryset = queryset.filter()
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)

    @action(detail=False)
    def feed(self, request, *args, **kwargs):
        """메인 화면에서 자신이 팔로우한 유저의 게시만"""
        return super().list(request, *args, **kwargs)
