from rest_framework import serializers

from posts.models import Post
from users.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    # owner = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'contents', 'owner')
        read_only_fields = ('id', 'owner')


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'img', 'post')
        read_only_fields = ('id',)
