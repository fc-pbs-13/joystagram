from time import sleep

from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils.models import TimeStampedModel
from redlock import Redlock

from users.models import User


class Follow(TimeStampedModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='followings')
    to_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ['owner', 'to_user']


@receiver(post_save, sender=Follow)
def update_follow_count(sender, instance=None, **kwargs):
    dlm = Redlock([{'host': 'localhost', 'port': 6379, 'db': 0}], retry_count=5)
    resource = f'Follow:{instance.id}'

    my_lock = dlm.lock(resource, 10000)
    if my_lock:
        instance.owner.profile.followers_count += 1
        instance.owner.profile.save()

        dlm.unlock(my_lock)
