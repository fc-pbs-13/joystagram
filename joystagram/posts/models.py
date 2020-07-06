from django.db import models


class Post(models.Model):
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    contents = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
