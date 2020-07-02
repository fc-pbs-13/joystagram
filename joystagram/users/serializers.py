from action_serializer import ModelActionSerializer
from rest_framework import serializers

from .models import User


class UserSerializer(ModelActionSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
        # action_fields = {
        #     'login': {'fields': ('email', 'password')},
        #     'update': {'fields': ('username', 'phoneNum', 'plateNum', 'cardNum',)},
        # }

    # def create(self, validated_data):
    #     user = super(UserSerializer, self).create(validated_data)
    #     # 이미 validation 과정이 마무리 되었으므로 password 필드는 반드시 있어야 함
    #     if 'password' in validated_data:
    #         user.set_password(validated_data['password'])
    #         user.save()
    #     return user
