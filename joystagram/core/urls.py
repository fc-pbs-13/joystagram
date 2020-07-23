from rest_framework_nested import routers

from comments.views import CommentViewSet, ReCommentViewSet, CommentCreateListViewSet, ReCommentCreateListViewSet
from likes.views import PostLikeViewSet, UserLikeViewSet
from posts.views import PostViewSet, TagViewSet, TaggedPostViewSet
from relationships.views import FollowViewSet
from story.views import StoryViewSet
from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'recomments', ReCommentViewSet)
router.register(r'follows', FollowViewSet)
router.register(r'story', StoryViewSet)
router.register(r'tags', TagViewSet)

posts_nested_router = routers.NestedSimpleRouter(router, r'posts', trailing_slash=False, lookup='post')
posts_nested_router.register(r'comments', CommentCreateListViewSet)
posts_nested_router.register(r'likes', PostLikeViewSet)

comments_nested_router = routers.NestedSimpleRouter(router, r'comments', trailing_slash=False, lookup='comment')
comments_nested_router.register(r'recomments', ReCommentCreateListViewSet)

users_nested_router = routers.NestedSimpleRouter(router, r'users', trailing_slash=False, lookup='user')
users_nested_router.register(r'follows', FollowViewSet)
users_nested_router.register(r'likes', UserLikeViewSet)

tags_nested_router = routers.NestedSimpleRouter(router, r'tags', trailing_slash=False, lookup='tag')
tags_nested_router.register(r'posts', TaggedPostViewSet)

urlpatterns = router.urls + posts_nested_router.urls + comments_nested_router.urls + \
              users_nested_router.urls + tags_nested_router.urls
