from django.db import models
from model_utils.models import TimeStampedModel


class Follow(TimeStampedModel):
    from_user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    to_user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['from_user', 'to_user']
