from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsPostOwner
from posts.models import Post
from posts.serializers import PostSerializer


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
