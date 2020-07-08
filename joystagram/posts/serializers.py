from rest_framework import serializers
from posts.models import Post, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('img',)


class PostSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'contents', 'owner', 'photos')
        read_only_fields = ('id', 'owner')

    def create(self, validated_data):
        """Post를 만든 후 이미지들로 Photo들 생성"""
        post = Post.objects.create(**validated_data)
        images_data = self.context['request'].FILES
        for image_data in images_data.getlist('photos'):
            # TODO 벌크로 한번에 쿼리하기
            Photo.objects.create(post=post, img=image_data)
        return post
