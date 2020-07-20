from rest_framework import serializers
from rest_framework.exceptions import NotFound
from relationships.models import Follow
from users.models import User
from users.serializers import SimpleProfileSerializer


class FollowSerializer(serializers.ModelSerializer):
    """팔로우 시리얼라이저"""

    user = SimpleProfileSerializer(source='to_user', required=False)

    class Meta:
        model = Follow
        fields = ('id', 'user')

    def validate(self, attrs):
        # user_pk lookup 검증
        to_user_pk = self.context['view'].kwargs.get('user_pk')
        if not to_user_pk or not User.objects.filter(id=to_user_pk).exists():
            raise NotFound('User is not valid')

        # UniqueTogether 검증
        if Follow.objects.filter(from_user=self.context['request'].user, to_user=to_user_pk).exists():
            raise serializers.ValidationError('The fields `from_user`, `to_user` must make a unique set.',
                                              code='unique')
        return attrs


class FollowUserListSerializer(serializers.ModelSerializer):
    follow_id = serializers.SerializerMethodField()
    nickname = serializers.CharField(max_length=20, source='profile.nickname')
    introduce = serializers.CharField(default='', source='profile.introduce')
    img = serializers.ImageField(read_only=True, source='profile.img')

    class Meta:
        model = User
        fields = ('id', 'nickname', 'introduce', 'img', 'follow_id')

    def get_follow_id(self, obj):
        follow_id = self.context['view'].follow_id_dict.get(obj.id)
        return follow_id
