from rest_framework import serializers
from rest_framework.exceptions import NotFound
from comments.models import Comment, ReComment
from posts.models import Post
from users.serializers import SimpleProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    owner = SimpleProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'owner', 'recomments', 'recomments_count')
        read_only_fields = ('owner', 'recomments', 'recomments_count')

    def validate(self, attrs):
        """post_pk 검증(nested url 일 때만 옴)"""
        if self.context['view'].action in ('create', 'list'):
            post_pk = self.context['view'].kwargs.get('post_pk')
            if not post_pk or not Post.objects.filter(id=post_pk).exists():
                raise NotFound('Post is not valid')
        return attrs


class CommentUpdateSerializer(serializers.ModelSerializer):
    owner = SimpleProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'owner', 'recomments', 'recomments_count')
        read_only_fields = ('owner', 'recomments', 'recomments_count')


class ReCommentSerializer(serializers.ModelSerializer):
    owner = SimpleProfileSerializer(read_only=True)

    class Meta:
        model = ReComment
        fields = ('id', 'content', 'comment_id', 'owner')
        read_only_fields = ('post_id', 'owner')

    def validate(self, attrs):
        """comment_pk 검증(nested url 일 때만 옴)"""
        if self.context['view'].action in ('create', 'list'):
            comment_pk = self.context['view'].kwargs.get('comment_pk')
            if not comment_pk or not Comment.objects.filter(id=comment_pk).exists():
                raise NotFound('Comment is not valid')
        return attrs


class ReCommentUpdateSerializer(serializers.ModelSerializer):
    owner = SimpleProfileSerializer(read_only=True)

    class Meta:
        model = ReComment
        fields = ('id', 'content', 'comment_id', 'owner')
        read_only_fields = ('post_id', 'owner')
