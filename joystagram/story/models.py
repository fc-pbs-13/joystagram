from django.db import models
from model_utils.models import TimeStampedModel


def story_img_path(instance, filename):
    return f'stories_img/{filename}'


class Story(TimeStampedModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to=story_img_path)
    duration = models.DurationField()


class StoryCheck(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    story = models.ForeignKey('stories.Story', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'story']
