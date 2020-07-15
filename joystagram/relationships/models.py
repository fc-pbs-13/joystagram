from django.db import models
from model_utils.models import TimeStampedModel


class Follow(TimeStampedModel):
    from_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='relations_from_me')
    to_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='relations_to_me')

    class Meta:
        unique_together = ['from_user', 'to_user']
