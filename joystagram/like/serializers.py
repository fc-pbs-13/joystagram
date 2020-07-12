from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from like.models import PostLike


class PostLikeUniqueTogetherValidator(UniqueTogetherValidator):
    """게시글 좋아요 UniqueTogether 검사"""

    def enforce_required_fields(self, attrs, serializer):
        attrs['user'] = serializer.context['request'].user
        super().enforce_required_fields(attrs, serializer)


class PostLikeSerializer(serializers.ModelSerializer):
    """게시글 좋아요 시리얼라이저"""
    class Meta:
        model = PostLike
        fields = ('id', 'post', 'owner')
        validators = [
            PostLikeUniqueTogetherValidator(
                queryset=PostLike.objects.all(),
                fields=('post', 'owner')
            )
        ]
