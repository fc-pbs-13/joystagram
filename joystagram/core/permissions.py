from rest_framework import permissions


class IsUserSelf(permissions.BasePermission):
    """유저 객체에 대한 권한(자기자신인지)"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    게시글, 댓글, 대댓글에 대한 권한
    생성: 로그인한 유저
    수정, 삭제: 업로더
    리스트: 모두
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method in ('PATCH', 'PUT', 'DELETE'):
            return obj.owner.user == request.user
        return super().has_permission(request, view)
