from action_serializer import ModelActionSerializer
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from users.models import User


class UserSerializer(ModelActionSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    points = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        action_fields = {
            'login': {'fields': ('email', 'password')},
            # 'update': {'fields': ('username', 'phoneNum', 'plateNum', 'cardNum',)},
        }

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'password')

    def validate(self, attrs):
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

    def validate_empty_values(self, data):
        return super().validate_empty_values(data)

# class UserLoginSerializer(AuthTokenSerializer):
#     email = serializers.CharField(label=_("Email"))
#     password = serializers.CharField(
#         label=_("Password"),
#         style={'input_type': 'password'},
#         trim_whitespace=False
#     )
#
#     def update(self, instance, validated_data):
#         pass
#
#     def create(self, validated_data):
#         pass
#
#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')
#
#         if email and password:
#             user = authenticate(request=self.context.get('request'),
#                                 email=email, password=password)
#
#             if not user:
#                 msg = _('Unable to log in with provided credentials.')
#                 raise serializers.ValidationError(msg, code='authorization')
#         else:
#             msg = _('Must include "username" and "password".')
#             raise serializers.ValidationError(msg, code='authorization')
#
#         attrs['user'] = user
#         return attrs
