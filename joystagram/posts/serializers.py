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
    photos = ListField(child=ImageField(), write_only=True)  # todo required=False 지우기
    _photos = PhotoSerializer(many=True, read_only=True, source='photos')
    owner = SimpleProfileSerializer(read_only=True)
    tags = TagListSerializerField()

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

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', '_photos', 'comments_count', 'likes_count', 'like_id', 'tags')
        read_only_fields = ('owner', 'likes_count', 'comments_count')

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
    # TODO 태그를 가진 Post
    class Meta:
        model = Tag
        fields = ('id', 'name')
