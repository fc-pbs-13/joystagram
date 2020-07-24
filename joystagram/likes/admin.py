from django.contrib import admin
from likes.models import PostLike


@admin.register(PostLike)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['owner', 'post']
    # fields = ['']
