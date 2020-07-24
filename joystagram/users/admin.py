"""Integrate with admin module."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = (
        'email', 'nickname', 'posts_count', 'comments_count', 'recomments_count', 'followers_count',
        'followings_count')
    search_fields = ('email', 'nickname')
    ordering = ('email',)

    def nickname(self, user):
        return user.profile.nickname

    def posts_count(self, user):
        return user.posts.count()

    def comments_count(self, user):
        return user.comments.count()

    def recomments_count(self, user):
        return user.recomments.count()

    def followers_count(self, user):
        return user.followers.count()

    def followings_count(self, user):
        return user.followings.count()
