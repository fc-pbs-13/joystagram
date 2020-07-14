from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from likes.models import PostLike
from likes.serializers import PostLikeSerializer


class PostLikeViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
    게시글 좋아요
    생성, 삭제
    POST, DELETE /api/posts/{post_id}/post_likes

    TODO url구성방안 2가지 중 고민
    생성,삭제,리스트 모두 nested? vs 생성이나 생성, 리스트만 nested
    """
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.profile.id,
                        post_id=self.kwargs['post_pk'])
