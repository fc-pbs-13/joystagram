from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueTogetherValidator

from likes.models import PostLike
from posts.models import Post
from relationships.models import Follow
from users.models import User
from users.serializers import SimpleProfileSerializer


class FollowSerializer(serializers.ModelSerializer):
    """팔로우 시리얼라이저"""

    user = SimpleProfileSerializer(source='to_user.profile', required=False)

    class Meta:
        model = Follow
        fields = ('id', 'user')

    def validate(self, attrs):
        # user_pk lookup 검증
        to_user_pk = self.context['view'].kwargs.get('to_user_pk')
        if not to_user_pk or not User.objects.filter(id=to_user_pk).exists():
            raise NotFound('User is not valid')

        # UniqueTogether 검증
        if Follow.objects.filter(from_user=self.context['request'].user,
                                 to_user=self.context['view'].kwargs['to_user_pk']).exists():
            raise serializers.ValidationError('The fields `from_user`, `to_user` must make a unique set.',
                                              code='unique')

        return super().validate(attrs)
