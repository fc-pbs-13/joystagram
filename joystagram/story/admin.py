from django.contrib import admin

from story.models import StoryCheck, Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'duration', 'created']


@admin.register(StoryCheck)
class StoryCheckAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'story', 'created']
