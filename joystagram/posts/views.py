from django.db.models import Q
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from core.permissions import IsOwnerOrReadOnly
from likes.models import PostLike
from posts.models import Post
from posts.serializers import PostSerializer, PostListSerializer
from relationships.models import Follow


class PostViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    """
    게시글 생성, 리스트, 수정, 삭제
    POST, GET
    /api/posts
    UPDATE, DELETE
    /api/posts/{post_id}
    """
    queryset = Post.objects.all().select_related('owner__profile').prefetch_related('photos')
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        if self.action == 'list':
            queryset = queryset.filter(
                Q(owner_id__in=Follow.objects.filter(from_user=self.request.user).values('to_user_id')) |
                Q(owner=self.request.user)
            )
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)

        # like_id 주입
        self.like_id_dict = {}
        if self.request.user.is_authenticated:
            like_list = PostLike.objects.filter(owner=self.request.user, post__in=page)
            self.like_id_dict = {like.post_id: like.id for like in like_list}
        return page
