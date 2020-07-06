from django.urls import path
from rest_framework import routers
from rest_framework.authtoken import views

from users.views import UserViewSet, ProfileViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
# router.register(r'profile', UserProfileViewSet)  # nested?

urlpatterns = router.urls
