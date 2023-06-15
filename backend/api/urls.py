
from django.urls import include, path, re_path
from rest_framework import routers

from api.views import FavoriteViewSet, IngredientViewSet, RecipeViewSet, TagViewSet,SubscriptionViewSet

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet, basename="ingridient")
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
)
router.register(r'xx', SubscriptionViewSet)



urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
