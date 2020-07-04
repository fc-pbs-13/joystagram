from action_serializer import ModelActionSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .models import User, UserProfile

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class UserSerializer(ModelActionSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

        action_fields = {
            'update': {
                'fields': ('username', 'password', 'email')
            },
        }


class UserAuthTokenSerializer(serializers.Serializer):
    """이메일, 비번으로 토큰 생성 시리얼라이저"""

    def update(self, instance, validated_data):
        pass

    email = serializers.EmailField()  # 모델의 email은 unique True이기 때문에 새로 선언
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def create(self, validated_data):
        """토큰 생성 with validated_data"""
        print(validated_data['user'], 'valid')
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = authenticate(
            email=email, password=password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    def validate(self, attrs):
        """"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(ModelActionSerializer):
    class Meta:
        model = User
        fields = ('id', 'introduce', 'img_url')
