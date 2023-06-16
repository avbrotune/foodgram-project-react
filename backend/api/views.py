from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from api.serializers import FavoriteSerializer, IngredientSerializer, RecipeSerializer, TagSerializer, SubscriptionSerializer
from recipes.models import Favorite, Ingredient, Recipe, Tag, Subscription
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            name = name.strip().lower()
            queryset = queryset.filter(name__startswith=name).union(
                queryset.filter(Q(name__contains=name) & ~Q(name__startswith=name)), all=True)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ["get", "post", "patch", "head", "delete"]
    # lookup_field = 'username'
    # search_fields = ['username', ]
    # ordering = ['id']

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited', None)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None)
        author = self.request.query_params.get('author', None)
        tags = self.request.query_params.getlist('tags', None)
        if is_favorited:
            if is_favorited == '1':
                queryset = queryset.filter(
                    favorites__user=self.request.user.id)
            else:
                queryset = queryset.exclude(
                    favorites__user=self.request.user.id)
        if is_in_shopping_cart:
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(shopping_carts__user=self.request.user.id)
            else:
                queryset = queryset.exclude(shopping_carts__user=self.request.user.id)
        if author:
            queryset = queryset.filter(author=author)
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__slug=tag)
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
        )


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()

    def create(self, serializer, **kwargs):
        user = self.request.user
        recipe = Recipe.objects.get(id=kwargs['recipe_id'])
        print(type(recipe))
        Favorite.objects.create(
            user=user,
            recipe=recipe,
        )
        data = {"id": recipe.id, "name": recipe.name}
        # serializer.save(recipe)
        return Response(data, status=status.HTTP_201_CREATED)
        # print(user)
        # print(recipe.name)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()



# from recipes.models import *
# q = Recipe.objects.get(id=1)
# q.ingredients.all()

# for ing in q.ingredients.all():
#     for am in ing.ingredient_amounts.all():
#         print(ing.name, ing.measurement_unit, am.amount)