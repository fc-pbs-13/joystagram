from django.db import models


class Post(models.Model):
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='posts')
    contents = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to='post_image')
