from django.db import models
from model_utils.models import TimeStampedModel


class Post(TimeStampedModel):
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(default='')


def post_img_path(instance, filename):
    return f'posts_img/{filename}'


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to=post_img_path)
