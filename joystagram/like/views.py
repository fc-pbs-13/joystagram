from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from like.models import PostLike
from like.serializers import PostLikeSerializer


class PostLikeViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        request.data['post_id'] = self.kwargs['post_pk']
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.profile.id, post_id=self.kwargs['post_pk'])
