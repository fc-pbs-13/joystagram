from action_serializer import ModelActionSerializer
from rest_framework import serializers

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
            # 'login': {
            #     'fields': ('email', 'password'),
            #     "extra_kwargs": {
            #         'password': {'write_only': True}
            #     }
            # },
            'update': {
                'fields': ('username', 'password', 'email')
            },
        }


class UserLoginSerializer(ModelActionSerializer):
    email = serializers.EmailField()

    # password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}


class UserProfileSerializer(ModelActionSerializer):
    class Meta:
        model = UserProfile
        fields = ('introduce', 'user')
        read_only_fields = ('user',)


class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
