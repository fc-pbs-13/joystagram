from rest_framework import serializers

from story.models import Story, StoryCheck
from users.serializers import SimpleProfileSerializer


class StorySerializer(serializers.ModelSerializer):
    _duration = serializers.IntegerField(read_only=True, source='duration.seconds')

    class Meta:
        model = Story
        fields = ('id', 'content', 'img', 'duration', '_duration')
        extra_kwargs = {
            'duration': {'write_only': True}
        }


class StoryListSerializer(serializers.ModelSerializer):
    _duration = serializers.IntegerField(source='duration.seconds')
    is_watched = serializers.SerializerMethodField()
    owner = SimpleProfileSerializer()

    class Meta:
        model = Story
        fields = ('id', 'content', 'img', '_duration', 'is_watched', 'owner')

    def get_is_watched(self, obj):
        # 이미 본 스토리인지
        return self.context['view'].story_check_dict.get(obj.id)
