from django.db import models
from model_utils.models import TimeStampedModel


class Post(TimeStampedModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(default='')
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)


def post_img_path(instance, filename):
    return f'post_img/{instance.post.owner.id}/{filename}'


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to=post_img_path)


class HashTag(models.Model):
    name = models.SlugField(unique=True)


class HashTaggedPost(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    tag = models.ForeignKey('posts.HashTag', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['post', 'story']
