from rest_framework import serializers
from posts.models import Post, Photo, Comment, ReComment
from users.serializers import ProfileSerializer


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'img')


class PostSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', 'photos', 'comments_count')
        read_only_fields = ('owner', 'comments_count')

    def create(self, validated_data):
        """Post를 만든 후 이미지들로 Photo들 생성"""
        post = Post.objects.create(**validated_data)
        images_data = self.context['request'].FILES

        photo_bulk_list = []
        for image_data in images_data.getlist('photos'):
            photo = Photo(post=post, img=image_data)
            photo_bulk_list.append(photo)
        Photo.objects.bulk_create(photo_bulk_list)

        return post

    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(read_only=True)
    recomments_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'content', 'post_id', 'owner', 'recomments', 'recomments_count')
        read_only_fields = ('post_id', 'owner', 'recomments', 'recomments_count')

    def create(self, validated_data):
        post = Post.objects.get(pk=self.context["view"].kwargs["post_pk"])
        validated_data["post"] = post
        return super().create(validated_data)

    def get_recomments_count(self, obj):
        return obj.recomments.count()


class ReCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReComment
        fields = ('id', 'content', 'comment_id', 'owner')
        read_only_fields = ('post_id', 'owner')
