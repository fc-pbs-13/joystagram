from rest_framework import serializers

from comments.models import Comment, ReComment
from posts.models import Post
from users.serializers import ProfileSerializer, SimpleProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    """TODO create, list 시리얼라이저 나누기"""
    owner = SimpleProfileSerializer(source='owner.profile', read_only=True)
    recomments_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'content', 'owner', 'recomments', 'recomments_count')
        read_only_fields = ('owner', 'recomments', 'recomments_count')

    def create(self, validated_data):
        post = Post.objects.get(pk=self.context["view"].kwargs["post_pk"])
        validated_data["post"] = post
        return super().create(validated_data)

    def get_recomments_count(self, obj):
        return obj.recomments.count()

    def validate(self, attrs):
        """post_id 검증"""
        if self.context['view'].action in ('create', 'list'):
            post_pk = self.context['view'].kwargs.get('post_pk')
            if not post_pk or not Post.objects.filter(id=post_pk).exists():
                raise serializers.ValidationError('Post is not valid')
        return super().validate(attrs)


class ReCommentSerializer(serializers.ModelSerializer):
    """TODO create, list 시리얼라이저 나누기"""
    owner = SimpleProfileSerializer(source='owner.profile', read_only=True)

    class Meta:
        model = ReComment
        fields = ('id', 'content', 'comment_id', 'owner')
        read_only_fields = ('post_id', 'owner')

    def validate(self, attrs):
        """comment_id 검증"""
        if self.context['view'].action in ('create', 'list'):
            comment_pk = self.context['view'].kwargs.get('comment_pk')
            if not comment_pk or not Comment.objects.filter(id=comment_pk).exists():
                raise serializers.ValidationError('Comment is not valid')
        return super().validate(attrs)
