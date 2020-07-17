from django.db import models
from model_utils.models import TimeStampedModel


def story_img_path(instance, filename):
    return f'stories_img/{filename}'


class Story(TimeStampedModel):
    content = models.TextField()
    img = models.ImageField(upload_to=story_img_path)
