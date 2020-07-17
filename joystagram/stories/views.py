from rest_framework import viewsets
from stories.models import Story, StoryCheck
from stories.serializers import StorySerializer


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
