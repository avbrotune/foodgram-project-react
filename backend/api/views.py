from django.db.models import Q
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import RecipeMiniSerializer, CustomUserSerializer, FavoriteSerializer, IngredientSerializer, RecipeSerializer, TagSerializer, SubscriptionSerializer
from recipes.models import Favorite, Ingredient, Recipe, Tag, Subscription, ShoppingCart
from users.models import User


class CustomUserViewSet(UserViewSet):

    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):

        queryset = User.objects.filter(subscriptions__user=self.request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        user = self.request.user
        author = self.get_object()
        if request.method == 'POST':
            sub = Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                sub.author, context={'request': request}, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            instance = get_object_or_404(
                Subscription, user=user, author=author)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


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
                queryset = queryset.filter(
                    shopping_carts__user=self.request.user.id)
            else:
                queryset = queryset.exclude(
                    shopping_carts__user=self.request.user.id)
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

    @action(['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        user = self.request.user
        recipe = self.get_object()
        if request.method == 'POST':
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            instance = get_object_or_404(Favorite, user=user, recipe=recipe)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        cart = ShoppingCart.objects.filter(user=user)
        res = dict()
        for cart_object in cart:
            for ingredient in cart_object.recipe.ingredients.all():
                for ingredient_recipe in ingredient.ingredient_amounts.filter(recipe=cart_object.recipe):
                    name = ingredient.name.capitalize()
                    if name in res:
                        res[name][1] += ingredient_recipe.amount
                    else:
                        res[name] = [ingredient.measurement_unit,
                                     ingredient_recipe.amount]
        with open('shopping_list.txt', 'w') as f:
            for obj in sorted(res.items()):
                f.write(f'{obj[0]} ({obj[1][0]}) - {obj[1][1]}\n')
            f.close()

            return Response(open('shopping_list.txt'), content_type='text/plain', status=status.HTTP_200_OK)

    @action(['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        recipe = self.get_object()
        if request.method == 'POST':
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            instance = get_object_or_404(
                ShoppingCart, user=user, recipe=recipe)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


# from recipes.models import *
# q = Recipe.objects.get(id=1)
# q.ingredients.all()

# for ing in q.ingredients.all():
#     for am in ing.ingredient_amounts.all():
#         print(ing.name, ing.measurement_unit, am.amount)

# User.objects.filter(user__subscriptions=request.user.id)


# ok
# from recipes.models import *
# q = ShoppingCart.objects.filter(user=1)
# res = dict()
# for cart_object in q:
#     for ingredient in cart_object.recipe.ingredients.all():
#         for ingredient_recipe in ingredient.ingredient_amounts.filter(recipe=cart_object.recipe):
        # name = ingredient.name
        # if name in res:
        #     res[name][1] += ingredient_recipe.amount
        # else:
        #     res[name] = [ingredient.measurement_unit, ingredient_recipe.amount]
# print(res)
# print(*sorted(res.items()))
        # print(ingredient.name, ingredient.measurement_unit, ingredient_recipe.amount)
