from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet

from likes.models import PostLike
from likes.serializers import PostLikeSerializer


class PostLikeViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
    게시글 좋아요
    생성, 리스트, 삭제
    POST, GET /api/posts/{post_id}/post_likes
    DELETE /api/posts/{post_id}/post_likes/{post_like_id}
    """
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.profile.id,
                        post_id=self.kwargs['post_pk'])
