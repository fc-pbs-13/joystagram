from django.contrib import admin
from relationships.models import Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_user', 'to_user']
