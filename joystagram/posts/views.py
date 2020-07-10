from django.http import QueryDict
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsPostOwner
from posts.models import Post, Comment, ReComment
from posts.serializers import PostSerializer, CommentSerializer, ReCommentSerializer


class PostViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsPostOwner]

    def get_permissions(self):
        if self.action in ('retrieve', 'list', 'thumbnails'):
            return [AllowAny()]
        return super().get_permissions()

    def filter_queryset(self, queryset):
        """
        TODO feed: 자신이 팔로우한 유저의 게시물만
        TODO thumbnails: 한 유저의 게시물만
        """
        qs = super().filter_queryset(queryset)
        if self.action == 'thumbnails':
            return qs.filter()
        if self.action == 'feed':
            return qs.filter()
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)

    @action(detail=False)
    def thumbnails(self, request, *args, **kwargs):
        """프로필 화면에서 게시물 대표사진 썸네일 목록
        TODO nested router를 써야하나? /api/users/{id}/posts
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False)
    def feed(self, request, *args, **kwargs):
        """메인 화면에서 자신이 팔로우한 유저의 게시만"""
        return super().list(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        print(self.kwargs['post_pk'])

        post_id = self.kwargs['post_pk']
        post = Post.objects.get(id=post_id)
        serializer.save(owner=self.request.user.profile,
                        post=post)


class ReCommentViewSet(viewsets.ModelViewSet):
    queryset = ReComment.objects.all()
    serializer_class = ReCommentSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # super().perform_create(serializer)
        comment_id = self.kwargs['comment_pk']
        comment = Comment.objects.get(id=comment_id)
        serializer.save(owner=self.request.user.profile,
                        comment=comment)
