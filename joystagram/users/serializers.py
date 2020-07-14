from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import User, Profile


class UserSerializer(ModelSerializer):
    nickname = serializers.CharField(max_length=20, source='profile.nickname')

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'nickname')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """유저 생성 시 프로필도 같이 생성"""
        profile = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile)
        return user


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


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'nickname', 'introduce', 'img')
