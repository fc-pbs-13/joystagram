from django.contrib import admin
from likes.models import PostLike


class LikeAdmin(admin.ModelAdmin):
    list_display = ['owner']
    fields = ['content', 'owner', 'likes_count', 'comments_count', 'tags']


admin.site.register(PostLike, LikeAdmin)
