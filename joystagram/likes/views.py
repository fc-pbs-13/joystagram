from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from likes.models import PostLike
from likes.serializers import LikeSerializer, UserLikedPostsSerializer, PostLikedUsersSerializer


class PostLikeViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
    생성, 삭제
    POST /api/posts/{post_id}/likes
    DELETE /api/posts/{post_id}/likes/{post_like_id}

    게시글에 좋아요한 유저 리스트
    GET /api/posts/{post_id}/likes
    """
    queryset = PostLike.objects.all().select_related('owner__profile', 'post__owner__profile')
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(post_id=self.kwargs['post_pk'])

    def get_serializer_class(self):
        if self.action == 'list':
            return PostLikedUsersSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id,
                        post_id=self.kwargs['post_pk'])


class UserLikeViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    유저가 좋아요한 게시글 리스트
    GET /api/users/{user_id}/likes
    """
    queryset = PostLike.objects.all().select_related('post__owner__profile').prefetch_related('post__photos')
    serializer_class = UserLikedPostsSerializer
    permission_classes = [IsAuthenticated]

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(owner_id=self.kwargs.get('user_pk'))
