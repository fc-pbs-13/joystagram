from django.core.cache import cache
from rest_framework import serializers
from rest_framework.fields import ListField, ImageField
from taggit.models import Tag

from posts.models import Post, Photo
from users.serializers import SimpleProfileSerializer
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'img')


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    photos = ListField(child=ImageField(), write_only=True)
    _photos = PhotoSerializer(many=True, read_only=True, source='photos')
    owner = SimpleProfileSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', 'photos', '_photos', 'tags')
        read_only_fields = ('owner',)

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


class PostListSerializer(serializers.ModelSerializer):
    _photos = PhotoSerializer(many=True, read_only=True, source='photos')
    like_id = serializers.SerializerMethodField(read_only=True)
    owner = SimpleProfileSerializer(read_only=True)
    tags = TagListSerializerField()

    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', '_photos', 'comments_count', 'likes_count', 'like_id', 'tags')
        read_only_fields = ('owner', 'likes_count', 'comments_count')

    def get_comments_count(self, obj):
        com_count_key = f'{obj.id}comments_count'
        count = cache.get(com_count_key)
        if count is None:
            count = obj.comments_count
            cache.set(com_count_key, count, 60)
        return count

    def get_likes_count(self, obj):
        like_count_key = f'{obj.id}likes_count'
        count = cache.get(like_count_key)
        if count is None:
            count = obj.likes_count
            cache.set(like_count_key, count, 60)
        return count

    def get_like_id(self, obj):
        like_id_dict = getattr(self.context['view'], 'like_id_dict', {})
        like_id = like_id_dict.get(obj.id)
        return like_id


class LikedPostSerializer(serializers.ModelSerializer):
    owner = SimpleProfileSerializer()
    _photos = PhotoSerializer(many=True, read_only=True, source='photos')

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', '_photos')
        read_only_fields = ('owner', 'likes_count')


class TagListSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'posts_count')

    def get_posts_count(self, obj):
        return obj.taggit_taggeditem_items.count()
