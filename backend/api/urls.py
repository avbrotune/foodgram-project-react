from django.urls import include, path, re_path
from rest_framework import routers

from api.views import TagViewSet

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
