from django.urls import path
from rest_framework import routers
from rest_framework.authtoken import views

from users.views import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)

urlpatterns = router.urls + [
    path(r'login', views.obtain_auth_token),
]