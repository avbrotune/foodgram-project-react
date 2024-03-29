from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.serializers import (RecipeCreatePatchSerializer, RecipeMiniSerializer,
                             IngredientSerializer, RecipeSerializer,
                             TagSerializer, SubscriptionSerializer)
from api.permissions import AdminOrAuthorOrReadOnly
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag, Subscription, ShoppingCart)
from users.models import User


class CustomUserViewSet(UserViewSet):

    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(
            subscriptions__user=self.request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            context={'request': request},
            many=True if page is not None else False
        )
        return self.get_paginated_response(
            serializer.data) if page else Response(
            serializer.data, status=status.HTTP_200_OK)

    @action(['post'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        '''Подписка на автора'''
        user = request.user
        author = self.get_object()
        serializer = SubscriptionSerializer(
            data={'author': author, 'user': user},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author, context={'request': request}, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, *args, **kwargs):
        '''Удаление подписки на автора'''
        user = self.request.user
        author = self.get_object()
        if Subscription.objects.filter(user=user, author=author).exists():
            instance = get_object_or_404(
                Subscription, user=user, author=author)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': "Подписка на пользователя отсутствует."},
            status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action in {'subscriptions', 'subscribe'}:
            return [IsAuthenticated(), ]
        return [AllowAny(), ]


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
                queryset.filter(Q(name__contains=name)
                                & ~Q(name__startswith=name)), all=True)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    http_method_names = ["get", "post", "patch", "head", "delete"]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited', None)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None)
        user = self.request.user.id
        author = self.request.query_params.get('author', None)
        tags = self.request.query_params.getlist('tags', None)
        if is_favorited and user:
            queryset = queryset.filter(
                favorites__user=user)
        if is_in_shopping_cart and user:
            queryset = queryset.filter(
                shopping_carts__user=user)
        if author:
            queryset = queryset.filter(author=author)
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__slug=tag)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST' or 'PATCH':
            return RecipeCreatePatchSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in {'favorite',
                           'download_shopping_cart', 'shopping_cart'}:
            return [IsAuthenticated(), ]
        return [AdminOrAuthorOrReadOnly(), ]

    @action(['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        user = self.request.user
        recipe = self.get_object()
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response({'error': "Рецепт уже добавлен в избранное."},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                instance = get_object_or_404(
                    Favorite, user=user, recipe=recipe)
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': "Рецепт отсутствует в избанном."},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_shopping_list(ingredient_list):
        content = []
        for obj in ingredient_list:
            name = obj["ingredient__name"]
            unit = obj["ingredient__measurement_unit"]
            amount = obj["ingredient_amount"]
            content.append(f'{name} ({unit}) - {amount}\r\n')
        return HttpResponse(
            content,
            content_type='text/plain',
            status=status.HTTP_200_OK)

    @action(['get'], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredient_list = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            ingredient_amount=Sum('amount')).order_by(
            'ingredient__name')
        return RecipeViewSet.create_shopping_list(ingredient_list)

    @action(['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        recipe = self.get_object()
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response({'error': "Рецепт уже есть в списке покупок."},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                instance = get_object_or_404(
                    ShoppingCart, user=user, recipe=recipe)
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': "Рецепт отсутствует в списке покупок."},
                            status=status.HTTP_400_BAD_REQUEST)
