from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from core.paginations import IDPagination
from core.permissions import IsOwnerOrReadOnly
from likes.models import PostLike
from posts.models import Post
from posts.serializers import PostSerializer, PostListSerializer


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

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        if self.action == 'list':
            queryset = queryset.filter()
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def paginate_queryset(self, queryset):
        # 모든 포스트
        page = super().paginate_queryset(queryset)
        # 해당 포스트의 좋아요중 내가 한것만
        self.like_id_dict = {}
        if self.request.user.is_authenticated:
            like_list = list(PostLike.objects.filter(owner=self.request.user, post__in=page))
            self.like_id_dict = {like.post_id: like.id for like in like_list}
        return page
