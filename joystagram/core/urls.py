from rest_framework import routers

from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
# router.register(r'profile', UserProfileViewSet)  # nested?

urlpatterns = router.urls
