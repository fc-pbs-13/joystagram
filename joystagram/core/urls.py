from rest_framework_nested import routers

from posts.views import PostViewSet, CommentViewSet, ReCommentViewSet
from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)

# TODO comments만 따로 열기 싫은데 네스티드는 얘를 등록해줘야한다고 하네...
router.register(r'comments', CommentViewSet)

comments_router = routers.NestedSimpleRouter(router, r'posts', trailing_slash=False, lookup='post')
comments_router.register(r'comments', CommentViewSet)

recomments_router = routers.NestedSimpleRouter(router, r'comments', trailing_slash=False, lookup='comment')
recomments_router.register(r'recomments', ReCommentViewSet)

urlpatterns = router.urls + comments_router.urls + recomments_router.urls
