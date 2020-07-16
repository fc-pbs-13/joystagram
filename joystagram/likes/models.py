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
        # 1
        self.post = F('likes_count') + 1
        self.post.save()
        # 2
        # Post.objects.filter(id=self.post.id).update(like_count=F('likes_count') + 1)
        super().save(force_insert, force_update, using, update_fields)
