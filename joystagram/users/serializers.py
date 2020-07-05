from action_serializer import ModelActionSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from .models import User, Profile


class UserSerializer(ModelActionSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.set_password(instance.password)
        instance.save()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


class LoginSerializer(serializers.Serializer):
    """유저 인증 시리얼라이저"""

    email = serializers.EmailField()  # 모델의 EmailField = unique True 때문에 새로 선언
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class ProfileSerializer(ModelActionSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'introduce', 'img_url')
        read_only_fields = ('id',)
