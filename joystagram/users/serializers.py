from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import User, Profile


class SimpleProfileSerializer(ModelSerializer):
    """함축 프로필 시리얼라이저 (닉네임, 프사)"""
    nickname = serializers.CharField(max_length=20, source='profile.nickname')
    introduce = serializers.CharField(default='', source='profile.introduce')
    img = serializers.ImageField(read_only=True, source='profile.img')

    class Meta:
        model = User
        fields = ('id', 'nickname', 'introduce', 'img')


class UserSerializer(ModelSerializer):
    nickname = serializers.CharField(max_length=20, source='profile.nickname')
    introduce = serializers.CharField(default='', source='profile.introduce')
    img = serializers.ImageField(read_only=True, source='profile.img')

    # 쿼리 4개씩??
    follow_id = serializers.SerializerMethodField(read_only=True)  # todo 이건 진짜 모르겠다
    posts_count = serializers.IntegerField(read_only=True, source='posts.count')
    followings_count = serializers.IntegerField(read_only=True, source='followings.count')
    followers_count = serializers.IntegerField(read_only=True, source='followers.count')

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'nickname', 'introduce', 'img', 'follow_id',
                  'posts_count', 'followings_count', 'followers_count')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """유저 생성 시 프로필도 같이 생성"""
        # todo 트랜잭션?
        profile = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile)
        return user

    def update(self, instance, validated_data):
        """프로필 업데이트"""
        profile = validated_data.pop('profile')
        Profile.objects.filter(user=instance).update(**profile)
        return instance

    def get_follow_id(self, to_user):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                return to_user.followers.get(owner=user).id
            except:
                pass
        return None


class UserPasswordSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        instance.password = validated_data['password']
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        label='Password',
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not (email and password):
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        user = authenticate(request=self.context.get('request'),
                            email=email, password=password)
        if user is None:
            msg = 'Unable to log in with provided credentials.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
