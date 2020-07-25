from rest_framework import serializers
from story.models import Story
from users.models import User
from users.serializers import SimpleProfileSerializer


class StorySerializer(serializers.ModelSerializer):
    _duration = serializers.IntegerField(read_only=True, source='duration.seconds')
    read_users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Story
        fields = ('id', 'content', 'img', 'duration', '_duration', 'created', 'read_users')
        extra_kwargs = {
            'duration': {'write_only': True}
        }

    def get_read_users(self, obj):
        """TODO 스토리를 본 유저들"""
        qs = User.objects.filter(storycheck__story__in=[obj])
        return SimpleProfileSerializer(qs, many=True).data


class StoryListSerializer(serializers.ModelSerializer):
    _duration = serializers.IntegerField(source='duration.seconds')
    watched = serializers.SerializerMethodField()
    owner = SimpleProfileSerializer()

    class Meta:
        model = Story
        fields = ('id', 'content', 'img', '_duration', 'watched', 'owner', 'created')

    def get_watched(self, obj):
        """이미 본 스토리인지: id 가 있으면 True"""
        story_check_dict = getattr(self.context['view'], 'story_check_dict', {})
        return story_check_dict.get(obj.id)
