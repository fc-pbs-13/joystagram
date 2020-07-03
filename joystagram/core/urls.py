from django.urls import path
from rest_framework import routers
from rest_framework.authtoken import views

from users.views import UserViewSet, UserProfileViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'profile', UserProfileViewSet)

urlpatterns = router.urls + [
    path(r'login', views.obtain_auth_token),
]
