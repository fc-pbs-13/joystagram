from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from relationships.models import Follow
from relationships.serializers import FollowSerializer


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    """
    팔로우
    생성, 리스트, 삭제
    POST, GET /api/users/{user_id}/follows
    DELETE /api/users/{user_id}/follows/{follows_id}
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(from_user_id=self.request.user.id,
                        to_user_id=self.kwargs['to_user_pk'])

    def filter_queryset(self, queryset):
        """TODO 비로그인 사용자의 팔로우 리스트"""
        if not isinstance(self.request.user, AnonymousUser):
            queryset = queryset.filter(from_user=self.request.user)
        return super().filter_queryset(queryset)
