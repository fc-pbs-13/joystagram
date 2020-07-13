from rest_framework import serializers

from comments.models import Comment, ReComment
from posts.models import Post
from users.serializers import ProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(read_only=True)
    recomments_count = serializers.SerializerMethodField()

    # best_recomment = serializers.SerializerMethodField()  # TODO 좋아요가 가장 많은 대댓글

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

    def get_best_recomment(self, obj):
        """좋아요가 가장 많은 대댓글"""
        pass


class ReCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReComment
        fields = ('id', 'content', 'comment_id', 'owner')
        read_only_fields = ('post_id', 'owner')
