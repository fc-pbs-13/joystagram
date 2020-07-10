from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include
from rest_framework_nested import routers

from posts.views import PostViewSet, CommentViewSet, ReCommentViewSet
from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

# 'base_name' is optional. Needed only if the same viewset is registered more than once
# Official DRF docs on this option: http://www.django-rest-framework.org/api-guide/routers/
comments_router = routers.NestedSimpleRouter(router, r'posts', trailing_slash=False, lookup='post')
comments_router.register(r'comments', CommentViewSet)

recomments_router = routers.NestedSimpleRouter(router, r'comments', trailing_slash=False, lookup='comment')
recomments_router.register(r'recomments', ReCommentViewSet)

urlpatterns = router.urls + comments_router.urls + recomments_router.urls
