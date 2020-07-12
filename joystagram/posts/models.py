from django.db import models
from model_utils.models import TimeStampedModel


class Post(TimeStampedModel):
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)


def post_img_path(instance, filename):
    return f'posts_img/{filename}'


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to=post_img_path)


class Comment(TimeStampedModel):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='comments')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=255)


class ReComment(TimeStampedModel):
    comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE, related_name='recomments')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='recomments')
    content = models.CharField(max_length=255)
