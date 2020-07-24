from django.db import models
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase, Tag


class Post(TimeStampedModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(default='')
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    tags = TaggableManager(blank=True)
    reported = models.BooleanField(default=False)


def post_img_path(instance, filename):
    return f'post_img/{instance.post.owner_id}/{filename}'


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to=post_img_path)
