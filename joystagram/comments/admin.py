from django.contrib import admin

from comments.models import Comment, ReComment


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'post', 'content']


class ReCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'comment', 'content']


admin.site.register(Comment, CommentAdmin)
admin.site.register(ReComment, ReCommentAdmin)
