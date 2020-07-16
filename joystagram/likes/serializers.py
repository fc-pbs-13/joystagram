from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from likes.models import PostLike
from posts.models import Post
from users.serializers import ProfileSerializer, SimpleProfileSerializer


class LikeSerializer(serializers.ModelSerializer):
    """게시글 좋아요 시리얼라이저"""
    owner = SimpleProfileSerializer(source='owner.profile', read_only=True)

    class Meta:
        model = PostLike
        fields = ('id', 'post_id', 'owner_id', 'owner')

    def validate(self, attrs):
        # post_pk lookup 검증
        post_pk = self.context['view'].kwargs.get('post_pk')
        if not post_pk or not Post.objects.filter(id=post_pk).exists():
            raise serializers.ValidationError('Post is not valid')

        # UniqueTogether 검증
        if PostLike.objects.filter(owner=self.context['request'].user, post=post_pk).exists():
            raise serializers.ValidationError('The fields `user`, `post` must make a unique set.',
                                              code='unique')

        return attrs
