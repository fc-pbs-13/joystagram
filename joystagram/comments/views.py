from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from comments.models import Comment, ReComment
from comments.serializers import CommentSerializer, ReCommentSerializer, ReCommentUpdateSerializer, \
    CommentUpdateSerializer
from core.permissions import IsOwnerOrReadOnly
from posts.models import Post


class CommentCreateListViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    """
    댓글 생성, 리스트
    POST, GET
    /api/posts/{post_id}/comments
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

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
    permission_classes = [IsOwnerOrReadOnly]


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
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """특정 Comment의 ReComment만"""
        return super().get_queryset().filter(post_id=self.kwargs.get('comment_pk'))

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
    permission_classes = [IsOwnerOrReadOnly]
