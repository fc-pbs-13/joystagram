from rest_framework import routers

from posts.views import PostViewSet
from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
# router.register(r'profile', UserProfileViewSet)  # nested?

urlpatterns = router.urls
