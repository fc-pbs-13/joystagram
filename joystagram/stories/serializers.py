from rest_framework import serializers

from stories.models import Story


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id',)
