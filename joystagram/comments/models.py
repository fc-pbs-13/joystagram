from django.db import models
from django.db.models import F
from model_utils.models import TimeStampedModel

from posts.models import Post


class Comment(TimeStampedModel):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='comments')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=255)
    recomments_count = models.PositiveIntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Post의 댓글 갯수 + 1"""
        super().save(force_insert, force_update, using, update_fields)
        Post.objects.filter(id=self.post.id).update(comments_count=F('comments_count') + 1)

    def delete(self, using=None, keep_parents=False):
        """Post의 댓글 갯수 - 1"""
        result = super().delete(using, keep_parents)
        Post.objects.filter(id=self.post.id).update(comments_count=F('comments_count') - 1)
        return result


class ReComment(TimeStampedModel):
    comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, related_name='recomments')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='recomments')
    content = models.CharField(max_length=255)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Post, Comment 의 댓글 갯수 + 1"""
        super().save(force_insert, force_update, using, update_fields)
        Post.objects.filter(id=self.comment.post.id).update(comments_count=F('comments_count') + 1)
        Comment.objects.filter(id=self.comment.id).update(recomments_count=F('recomments_count') + 1)

    def delete(self, using=None, keep_parents=False):
        """Post, Comment 의 댓글 갯수 - 1"""
        result = super().delete(using, keep_parents)
        Post.objects.filter(id=self.comment.post.id).update(comments_count=F('comments_count') - 1)
        Comment.objects.filter(id=self.comment.id).update(recomments_count=F('recomments_count') - 1)
        return result
