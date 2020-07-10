from rest_framework import serializers
from posts.models import Post, Photo, Comment, ReComment
from users.serializers import ProfileSerializer


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'img')


class PostSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', 'photos')
        read_only_fields = ('owner',)

    def create(self, validated_data):
        """Post를 만든 후 이미지들로 Photo들 생성"""
        post = Post.objects.create(**validated_data)
        images_data = self.context['request'].FILES
        for image_data in images_data.getlist('photos'):
            # TODO 벌크로 한번에 쿼리하기
            Photo.objects.create(post=post, img=image_data)
        return post


class CommentSerializer(serializers.ModelSerializer):
    """TODO 대댓글 개수도 보여주기"""

    owner = ProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'post_id', 'owner', 'recomments')
        read_only_fields = ('post_id', 'owner', 'recomments')

    def create(self, validated_data):
        post = Post.objects.get(pk=self.context["view"].kwargs["post_pk"])
        validated_data["post"] = post
        return super().create(validated_data)


class ReCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReComment
        fields = ('id', 'content', 'comment_id', 'owner')
        read_only_fields = ('post_id', 'owner')
