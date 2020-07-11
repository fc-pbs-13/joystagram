from rest_framework import permissions


class IsUserSelf(permissions.BasePermission):
    """유저 객체에 대한 권한(자기자신인지)"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsPostOwner(permissions.BasePermission):
    """포스트에 대한 권한"""

    def has_object_permission(self, request, view, obj):
        return obj.owner.user == request.user
