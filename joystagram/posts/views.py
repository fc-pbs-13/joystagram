from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from core.permissions import IsOwnerOrAuthenticatedReadOnly
from likes.models import PostLike
from posts.models import Post
from posts.serializers import PostSerializer, PostListSerializer
from relationships.models import Follow


# class TagFilter(filters.FilterSet):
#     tag = filters.NumberFilter(field_name="price", lookup_expr='gte')
#
#     class Meta:
#         model = Post
#         fields = ['tags']


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
    filter_backends = [DjangoFilterBackend]
    # filterset_class = TagFilter  # TODO 태그로 검색

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
        self.like_id_dict = {}
        if self.request.user.is_authenticated:
            like_list = PostLike.objects.filter(owner=self.request.user, post__in=page)
            self.like_id_dict = {like.post_id: like.id for like in like_list}
        return page

# class TagAPIView(mixins.ListModelMixin, GenericAPIView):
#     queryset = HashTag
#     serializer_class =
