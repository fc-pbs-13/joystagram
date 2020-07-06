from rest_framework import mixins
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
        if self.action in ('retrieve', 'list',):
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)
