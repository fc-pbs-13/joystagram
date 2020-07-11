from rest_framework_nested import routers

from posts.views import PostViewSet, CommentCreateListViewSet, ReCommentCreateListViewSet, CommentViewSet, ReCommentViewSet
from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
# router.register(r'recomments', ReCommentViewSet)

comments_router = routers.NestedSimpleRouter(router, r'posts', trailing_slash=False, lookup='post')
comments_router.register(r'comments', CommentCreateListViewSet)

recomments_router = routers.NestedSimpleRouter(router, r'comments', trailing_slash=False, lookup='comment')
recomments_router.register(r'recomments', ReCommentCreateListViewSet)

urlpatterns = router.urls + comments_router.urls + recomments_router.urls
