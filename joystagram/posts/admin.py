from django.contrib import admin
from django.utils.safestring import mark_safe

from posts.models import Post, Photo


def report(modeladmin, request, queryset):
    queryset.update(reported=True)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'content', 'reported', 'likes_count', 'comments_count']
    list_filter = ['created', 'likes_count', 'comments_count']
    actions = [report]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'post']
    readonly_fields = ['image']

    def image(self, obj):
        return mark_safe(f'<img src="{obj.img.url}" width="{obj.img.width}" height={obj.img.width} />')
