from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from relationships.models import Follow
from .models import User, Profile


class ProfileSerializer(ModelSerializer):
    """프로필 시리얼라이저"""

    class Meta:
        model = Profile
        fields = ('id', 'nickname', 'introduce', 'img')


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
    follow_id = serializers.SerializerMethodField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True, source='posts.count')
    followers_count = serializers.IntegerField(read_only=True, source='followers.count')
    followings_count = serializers.IntegerField(read_only=True, source='followings.count')

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'nickname', 'introduce', 'img', 'follow_id', 'posts_count',
                  'followers_count', 'followings_count')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """유저 생성 시 프로필도 같이 생성"""
        profile = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile)
        return user

    def update(self, instance, validated_data):
        """프로필 업데이트"""
        profile = validated_data.pop('profile')
        Profile.objects.filter(user=instance).update(**profile)
        return instance

    def get_follow_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                return Follow.objects.get(from_user=user, to_user=obj).id
            except ObjectDoesNotExist:
                pass
        return None


class UserPasswordSerializer(ModelSerializer):
    """password 변경 시리얼라이저"""

    class Meta:
        model = User
        fields = ('password',)
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        instance.password = validated_data['password']
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """유저 인증 시리얼라이저"""

    email = serializers.EmailField()
    password = serializers.CharField(
        label='Password',
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if user is None:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
