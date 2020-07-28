from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from comments.models import Comment, ReComment
from core.permissions import IsOwnerOrAuthenticatedReadOnly
from comments.serializers import CommentSerializer, ReCommentSerializer, ReCommentUpdateSerializer, \
    CommentUpdateSerializer


class CommentCreateListViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    """
    댓글 생성, 리스트
    POST, GET
    /api/posts/{post_id}/comments
    """
    queryset = Comment.objects.all().select_related('owner__profile').prefetch_related('recomments')
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]

    def get_queryset(self):
        """특정 Post의 Comment만"""
        return super().get_queryset().filter(post_id=self.kwargs.get('post_pk'))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, post_id=self.kwargs.get('post_pk'))


class CommentViewSet(mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    """
    댓글 수정, 삭제
    PATCH, DELETE
    /api/comments/{comments_id}"""
    queryset = Comment.objects.all().prefetch_related()
    serializer_class = CommentUpdateSerializer
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]


class ReCommentCreateListViewSet(mixins.CreateModelMixin,
                                 mixins.ListModelMixin,
                                 GenericViewSet):
    """
    대댓글 생성, 리스트
    POST, GET
    /api/comments/{comments_id}/recomments
    """
    queryset = ReComment.objects.all()
    serializer_class = ReCommentSerializer
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(comment_id=self.kwargs.get('comment_pk'))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, comment_id=self.kwargs['comment_pk'])


class ReCommentViewSet(mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       GenericViewSet):
    """
    대댓글 수정, 삭제
    PATCH, DELETE
    /api/recomments/{recomments_id}
    """
    queryset = ReComment.objects.all()
    serializer_class = ReCommentUpdateSerializer
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]
