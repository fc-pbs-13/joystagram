from rest_framework_nested import routers

from comments.views import CommentViewSet, ReCommentViewSet, CommentCreateListViewSet, ReCommentCreateListViewSet
from likes.views import PostLikeViewSet
from posts.views import PostViewSet
from relationships.views import FollowViewSet
from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'recomments', ReCommentViewSet)
router.register(r'follows', FollowViewSet)

comments_router = routers.NestedSimpleRouter(router, r'posts', trailing_slash=False, lookup='post')
comments_router.register(r'comments', CommentCreateListViewSet)
comments_router.register(r'post_likes', PostLikeViewSet)

recomments_router = routers.NestedSimpleRouter(router, r'comments', trailing_slash=False, lookup='comment')
recomments_router.register(r'recomments', ReCommentCreateListViewSet)

follows_router = routers.NestedSimpleRouter(router, r'users', trailing_slash=False, lookup='to_user')
follows_router.register(r'follows', FollowViewSet)

urlpatterns = router.urls + comments_router.urls + recomments_router.urls + follows_router.urls
