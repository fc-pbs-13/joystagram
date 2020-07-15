from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueTogetherValidator

from likes.models import PostLike
from posts.models import Post
from relationships.models import Follow
from users.models import User
from users.serializers import SimpleProfileSerializer


class FollowUniqueTogetherValidator(UniqueTogetherValidator):

    def enforce_required_fields(self, attrs, serializer):
        """게시글 좋아요 UniqueTogether 검사"""
        attrs['from_user_id'] = serializer.context['request'].user.id
        attrs['to_user_id'] = serializer.context['view'].kwargs['to_user_pk']
        super().enforce_required_fields(attrs, serializer)


class FollowSerializer(serializers.ModelSerializer):
    """팔로우 시리얼라이저"""
    to_user = SimpleProfileSerializer(source='to_user.profile', read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'to_user', 'from_user_id', 'to_user_id')
        # extra_kwargs = {
        #     'from_user_id': {'write_only': True},
        #     'to_user_id': {'write_only': True}
        # }
        validators = [
            FollowUniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('from_user_id', 'to_user_id')
            )
        ]

    def validate(self, attrs):
        """user_pk 검증"""
        to_user_pk = self.context['view'].kwargs.get('to_user_pk')
        if not to_user_pk or not User.objects.filter(id=to_user_pk).exists():
            raise NotFound('User is not valid')
        return super().validate(attrs)
