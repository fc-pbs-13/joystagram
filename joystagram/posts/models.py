from django.db import models
from model_utils.models import TimeStampedModel


class Post(TimeStampedModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(default='')
    likes_count = models.PositiveIntegerField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            self.likes_count = 0
        super().save(force_insert, force_update, using, update_fields)


def post_img_path(instance, filename):
    return f'post_img/{instance.post.owner.id}/{filename}'


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to=post_img_path)
