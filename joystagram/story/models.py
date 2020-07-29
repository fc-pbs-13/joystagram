from django.core.cache import cache
from django.db import models
from model_utils.models import TimeStampedModel


def story_img_path(instance, filename):
    return f'story_img/{instance.owner_id}/{filename}'


class Story(TimeStampedModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to=story_img_path)
    duration = models.DurationField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id:
            key = f'{self.id}story'
            cache.delete(key)
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        key = f'{self.id}story'
        cache.delete(key)
        return super().delete(using, keep_parents)


class StoryCheck(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    story = models.ForeignKey('story.Story', on_delete=models.CASCADE, related_name='story_checks')

    class Meta:
        unique_together = ['user', 'story']
