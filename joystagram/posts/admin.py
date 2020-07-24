from django.contrib import admin
from posts.models import Post, Photo


def report(modeladmin, request, queryset):
    queryset.update(reported=True)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'content', 'reported', 'likes_count', 'comments_count']
    list_filter = ['created', 'likes_count', 'comments_count']
    # fields = ['content', 'owner', 'likes_count', 'comments_count', 'tags']
    actions = [report]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'post']
    # fields = ['content', 'owner', 'likes_count', 'comments_count', 'tags']
