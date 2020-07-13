from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from core.paginations import IDPagination
from core.permissions import IsOwnerOrReadOnly
from posts.models import Post, Comment, ReComment
from posts.serializers import PostSerializer, CommentSerializer, ReCommentSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    게시글 생성, 리스트, 수정, 삭제
    POST, GET
    /api/posts
    UPDATE, DELETE
    /api/posts/{post_id}
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]

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

    # @action(detail=False)
    # def thumbnails(self, request, *args, **kwargs):
    #     """프로필 화면에서 게시물 대표사진 썸네일 목록"""
    #     return super().list(request, *args, **kwargs)
    #
    # @action(detail=False)
    # def feed(self, request, *args, **kwargs):
    #     """메인 화면에서 자신이 팔로우한 유저의 게시만"""
    #     return super().list(request, *args, **kwargs)


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
