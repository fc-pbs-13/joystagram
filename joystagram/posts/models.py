from django.db import models
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager


class Post(TimeStampedModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(default='')
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    tags = TaggableManager()


def post_img_path(instance, filename):
    return f'post_img/{instance.post.owner.id}/{filename}'


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to=post_img_path)


# class HashTag(models.Model):
#     """
#     TODO 태그 구현...
#     포스트 생성시 HashTag get_or_create()
#     태그가 여러개 so N+1문제 고려
#
#     """
#     name = models.SlugField(unique=True)
#
#
# class HashTaggedPost(models.Model):
#     post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
#     tag = models.ForeignKey('posts.HashTag', on_delete=models.CASCADE)
#
#     class Meta:
#         unique_together = ['post', 'tag']
