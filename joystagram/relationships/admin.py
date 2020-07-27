from django.contrib import admin
from relationships.models import Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'to_user']
