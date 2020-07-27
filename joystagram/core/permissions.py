from rest_framework import permissions


class IsUserSelf(permissions.IsAuthenticated):
    """유저 자신에 대한 권한"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwnerOrAuthenticatedReadOnly(permissions.IsAuthenticated):
    """
    생성, 조회: IsAuthenticated
    수정, 삭제: IsOwner
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
