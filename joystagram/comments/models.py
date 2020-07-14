from django.db import models
from model_utils.models import TimeStampedModel


class Comment(TimeStampedModel):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='comments')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=255)


class ReComment(TimeStampedModel):
    comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, related_name='recomments')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='recomments')
    content = models.CharField(max_length=255)
