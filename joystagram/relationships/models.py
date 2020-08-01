from django.db import models
from model_utils.models import TimeStampedModel


class Follow(TimeStampedModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='followings')
    to_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ['owner', 'to_user']
