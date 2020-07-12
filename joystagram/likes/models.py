from django.db import models


class PostLike(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='likes')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='post_likes')

    class Meta:
        unique_together = ['owner', 'post']


class CommentLike(models.Model):
    comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE, related_name='likes')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='comment_likes')

    class Meta:
        unique_together = ['owner', 'comment']


class ReCommentLike(models.Model):
    recomment = models.ForeignKey('posts.ReComment', on_delete=models.CASCADE, related_name='likes')
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='recomment_likes')

    class Meta:
        unique_together = ['owner', 'recomment']
