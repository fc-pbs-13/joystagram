from django.db import models
from django.db.models import F
from model_utils.models import TimeStampedModel

from posts.models import Post


class PostLike(TimeStampedModel):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='likes')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='post_likes')

    class Meta:
        unique_together = ['owner', 'post']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Post의 좋아요 갯수 + 1"""
        Post.objects.filter(id=self.post.id).update(likes_count=F('likes_count') + 1)
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        """Post의 좋아요 갯수 - 1"""
        Post.objects.filter(id=self.post.id).update(likes_count=F('likes_count') - 1)
        return super().delete(using, keep_parents)
