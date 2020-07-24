from rest_framework import permissions


class IsUserSelf(permissions.BasePermission):
    """유저 객체에 대한 권한(자기자신인지)"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwnerOrAuthenticatedReadOnly(permissions.BasePermission):
    """
    생성, 조회: IsAuthenticated
    수정, 삭제: IsOwner
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsFromUserOrReadOnly(permissions.BasePermission):
    """
    생성, 조회: IsAuthenticated
    수정, 삭제: IsFromUser
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.from_user == request.user
