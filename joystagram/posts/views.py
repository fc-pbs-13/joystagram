from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

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

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

