from django.db import models


class Post(models.Model):
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='posts')
    contents = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)


def post_img_path(instance, filename):
    return f'posts_img/{filename}'


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to=post_img_path)


# 에러 발생
# posts.ReComment.comment: (models.E006) The field 'comment' clashes with the field 'comment' from model 'posts.basecomment'.
# class BaseComment(models.Model):
#     """댓글, 대댓글 베이스 모델"""
#     content = models.CharField(max_length=255)
#     created = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class ReComment(models.Model):
    comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
