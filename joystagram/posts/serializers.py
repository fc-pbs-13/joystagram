from rest_framework import serializers

from posts.models import Post
from users.serializers import UserSerializer


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'img', 'post')
        read_only_fields = ('id', 'post')


class PostSerializer(serializers.ModelSerializer):
    # owner = UserSerializer(read_only=True)
    photos = PhotoSerializer(many=True)

    class Meta:
        model = Post
        fields = ('id', 'contents', 'owner', 'photos')
        read_only_fields = ('id', 'owner')

    def validate(self, attrs):
        print(attrs, 'post validate')
        return super().validate(attrs)
