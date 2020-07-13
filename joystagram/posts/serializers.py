from rest_framework import serializers
from rest_framework.fields import ListField, ImageField

from posts.models import Post, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'img')


class PostSerializer(serializers.ModelSerializer):
    photos = ListField(child=ImageField(), write_only=True)
    _photos = PhotoSerializer(many=True, read_only=True, source='photos')
    comments_count = serializers.SerializerMethodField()
    # best_comment = serializers.SerializerMethodField()  # TODO 좋아요가 가장 많은 댓글

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', 'photos', '_photos', 'comments_count')
        read_only_fields = ('owner', 'comments_count')

    def create(self, validated_data):
        """Post를 만든 후 이미지들로 Photo들 생성"""
        photos = validated_data.pop('photos')
        post = Post.objects.create(**validated_data)
        photo_bulk_list = []
        for image_data in photos:
            photo = Photo(post=post, img=image_data)
            photo_bulk_list.append(photo)
        Photo.objects.bulk_create(photo_bulk_list)

        return post

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_best_comment(self, obj):
        """좋아요가 가장 많은 댓글"""
        pass
