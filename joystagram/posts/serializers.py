from django.db import models
from rest_framework import serializers
from rest_framework.fields import ListField, ImageField

from likes.models import PostLike
from posts.models import Post, Photo
from users.serializers import SimpleProfileSerializer


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'img')


class PostSerializer(serializers.ModelSerializer):
    # TODO 모델의 필드에 좋아요 갯수 저장
    photos = ListField(child=ImageField(), write_only=True)
    _photos = PhotoSerializer(many=True, read_only=True, source='photos')
    comments_count = serializers.SerializerMethodField(read_only=True)
    liked = serializers.SerializerMethodField(read_only=True)
    like_id = serializers.SerializerMethodField(read_only=True)
    owner = SimpleProfileSerializer(source='owner.profile', read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', 'photos', '_photos', 'comments_count', 'likes_count', 'liked', 'like_id')
        read_only_fields = ('owner', 'likes_count')

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
        """댓글 갯수"""
        return obj.comments.count()

    def get_liked(self, obj) -> bool:
        """이 사용자가 게시글에 좋아요를 했는지"""
        try:
            return obj.likes.filter(owner=self.context['request'].user).exists()
        except (models.ObjectDoesNotExist, TypeError):
            return False

    def get_like_id(self, obj):
        """좋아요 했다면 id 반환 아니면 None"""
        try:
            post_like = PostLike.objects.get(owner=self.context['request'].user, post=obj)
            return post_like.id
        except (models.ObjectDoesNotExist, TypeError):
            return None
