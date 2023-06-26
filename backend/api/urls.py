from django.urls import include, path
from rest_framework import routers
from api.views import (
    CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet)

router = routers.DefaultRouter()

router.register(r'users', CustomUserViewSet, basename="user")
router.register(r'tags', TagViewSet, basename="tag")
router.register(r'recipes', RecipeViewSet, basename="recipe")
router.register(r'ingredients', IngredientViewSet, basename="ingridient")

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
