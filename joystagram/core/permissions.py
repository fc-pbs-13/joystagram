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
        return obj.owner_id == request.user.id


class IsFromUserOrReadOnly(permissions.BasePermission):
    """
    생성, 조회: IsAuthenticated
    수정, 삭제: IsFromUser
    TODO from_user -> owner 변경해서 클래스 통합 고려
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.from_user_id == request.user.id


# class IsStoryOwner(permissions.BasePermission):
#     # TODO 내 스토리인지 검사
#     def has_object_permission(self, request, view, obj):
#         view.kwargs.get('story_pk')
#         return super().has_object_permission(request, view, obj)
