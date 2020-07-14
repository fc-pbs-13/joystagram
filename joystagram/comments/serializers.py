from rest_framework import serializers

from comments.models import Comment, ReComment
from posts.models import Post
from users.serializers import ProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(read_only=True)
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


class ReCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReComment
        fields = ('id', 'content', 'comment_id', 'owner')
        read_only_fields = ('post_id', 'owner')
