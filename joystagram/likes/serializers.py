from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from likes.models import PostLike
from posts.models import Post
from users.serializers import ProfileSerializer


class PostLikeUniqueTogetherValidator(UniqueTogetherValidator):

    def enforce_required_fields(self, attrs, serializer):
        """게시글 좋아요 UniqueTogether 검사"""
        attrs['owner_id'] = serializer.context['request'].user.profile.id
        attrs['post_id'] = serializer.context['view'].kwargs['post_pk']
        super().enforce_required_fields(attrs, serializer)


class PostLikeSerializer(serializers.ModelSerializer):
    """게시글 좋아요 시리얼라이저"""
    owner = ProfileSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ('id', 'post_id', 'owner_id', 'owner')
        validators = [
            PostLikeUniqueTogetherValidator(
                queryset=PostLike.objects.all(),
                fields=('post_id', 'owner_id')
            )
        ]

    def validate(self, attrs):
        """post_id 검증"""
        post_pk = self.context['view'].kwargs.get('post_pk')
        if not post_pk or not Post.objects.filter(id=post_pk).exists():
            raise serializers.ValidationError('Post is not valid')
        return super().validate(attrs)
