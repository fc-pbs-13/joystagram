from django.db import models
from model_utils.models import TimeStampedModel


class PostLike(TimeStampedModel):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='likes')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='post_likes')

    class Meta:
        unique_together = ['owner', 'post']


class CommentLike(TimeStampedModel):
    comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, related_name='likes')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='comment_likes')

    class Meta:
        unique_together = ['owner', 'comment']


class ReCommentLike(TimeStampedModel):
    recomment = models.ForeignKey('comments.ReComment', on_delete=models.CASCADE, related_name='likes')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='recomment_likes')

    class Meta:
        unique_together = ['owner', 'recomment']
