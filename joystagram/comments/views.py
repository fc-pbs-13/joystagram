from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from comments.models import Comment, ReComment
from comments.serializers import CommentSerializer, ReCommentSerializer
from core.permissions import IsOwnerOrReadOnly


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

    def perform_create(self, serializer):
        """get_object_or_404???"""
        post_id = self.kwargs['post_pk']
        serializer.save(owner=self.request.user.profile,
                        post_id=post_id)


class CommentViewSet(mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    """
    댓글 수정, 삭제
    PATCH, DELETE
    /api/comments/{comments_id}"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
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

    def perform_create(self, serializer):
        comment_id = self.kwargs['comment_pk']
        serializer.save(owner=self.request.user.profile,
                        comment_id=comment_id)


class ReCommentViewSet(mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       GenericViewSet):
    """
    대댓글 수정, 삭제
    PATCH, DELETE
    /api/recomments/{recomments_id}
    """
    queryset = ReComment.objects.all()
    serializer_class = ReCommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
