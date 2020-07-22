from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from taggit.models import Tag

from core.permissions import IsOwnerOrAuthenticatedReadOnly
from likes.models import PostLike
from posts.models import Post
from posts.serializers import PostSerializer, PostListSerializer, TagListSerializer
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
    permission_classes = [IsOwnerOrAuthenticatedReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        """자신과 자신이 팔로우하는 유저들의 스토리(등록시간 24시간 이내)"""
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
        if self.request.user.is_authenticated:
            like_list = PostLike.objects.filter(owner=self.request.user, post__in=page)
            self.like_id_dict = {like.post_id: like.id for like in like_list}
        return page


class TagViewSet(mixins.ListModelMixin,
                 GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        return self.queryset.filter(name__icontains=name)
