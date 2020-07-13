from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from likes.models import PostLike


class PostLikeUniqueTogetherValidator(UniqueTogetherValidator):

    def enforce_required_fields(self, attrs, serializer):
        """게시글 좋아요 UniqueTogether 검사"""
        attrs['owner_id'] = serializer.initial_data['owner_id']
        attrs['post_id'] = serializer.initial_data['post_id']
        super().enforce_required_fields(attrs, serializer)


class PostLikeSerializer(serializers.ModelSerializer):
    """게시글 좋아요 시리얼라이저"""

    class Meta:
        model = PostLike
        fields = ('id', 'post_id', 'owner_id')
        validators = [
            PostLikeUniqueTogetherValidator(
                queryset=PostLike.objects.all(),
                fields=('post_id', 'owner_id')
            )
        ]


# class CommentLikeUniqueTogetherValidator(UniqueTogetherValidator):
#     """댓글 좋아요 UniqueTogether 검사"""
#
#     def enforce_required_fields(self, attrs, serializer):
#         attrs['owner_id'] = serializer.context['request'].user.profile.id
#         attrs['comment_id'] = serializer.context['view'].kwargs['comment_pk']
#         super().enforce_required_fields(attrs, serializer)
#
#
# class CommentLikeSerializer(serializers.ModelSerializer):
#     """댓글 좋아요 시리얼라이저"""
#
#     class Meta:
#         model = PostLike
#         fields = ('id', 'comment_id', 'owner_id')
#         validators = [
#             PostLikeUniqueTogetherValidator(
#                 queryset=PostLike.objects.all(),
#                 fields=('comment_id', 'owner_id')
#             )
#         ]
