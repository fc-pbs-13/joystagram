from django.contrib import admin

from comments.models import Comment, ReComment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'post', 'content']


@admin.register(ReComment)
class ReCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'comment', 'content']
