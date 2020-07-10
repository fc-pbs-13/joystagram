from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from posts.views import PostViewSet, CommentViewSet, ReCommentViewSet
from users.views import UserViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)

# 'base_name' is optional. Needed only if the same viewset is registered more than once
# Official DRF docs on this option: http://www.django-rest-framework.org/api-guide/routers/
domains_router = NestedSimpleRouter(router, r'posts', trailing_slash=False, lookup='post')
domains_router.register(r'comments', CommentViewSet)

urlpatterns = (
    url(r'^', include(router.urls)),
    url(r'^', include(domains_router.urls)),
)
# urls.py


