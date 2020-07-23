from django.contrib import admin

from posts.models import Post


class PostAdmin(admin.ModelAdmin):
    fields = ['content', 'owner', 'likes_count', 'comments_count', 'tags']


admin.site.register(Post, PostAdmin)
