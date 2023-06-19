from django.urls import include, path
from rest_framework import routers


from api.views import (
    CustomUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    SubscriptionViewSet
)


router = routers.DefaultRouter()

router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet, basename="ingridient")
router.register(r'xx',SubscriptionViewSet)

urlpatterns = [
    # path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
