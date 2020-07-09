from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from posts.views import PostViewSet
from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)

urlpatterns = router.urls
