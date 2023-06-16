import base64

from django.core.files.base import ContentFile
from djoser.serializers import TokenCreateSerializer, UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.models import Favorite, Ingredient, IngredientRecipe, Recipe, Tag, Subscription
from users.models import User


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )


class CustomUserSerializer(UserSerializer):

    def is_sub(self, instance):
        user = self.context['request'].user
        author = instance.id
        try:
            return user.subscriber.filter(author=author).exists()
        except Exception:
            return False

    is_subscribed = SerializerMethodField(method_name='is_sub')

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "id",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = IngredientSerializer(many=False, read_only=False)
    name = IngredientSerializer(many=True, read_only=False)
    measurement_unit = IngredientSerializer(many=True, read_only=False)

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        depth = 1


class RecipeSerializer(serializers.ModelSerializer):

    def is_fav(self, instance):
        user = self.context['request'].user
        recipe = instance.id
        try:
            return user.favorites.filter(recipe=recipe).exists()
        except Exception:
            return False

    def is_in_cart(self, instance):
        user = self.context['request'].user
        recipe = instance.id
        try:
            return user.shopping_carts.filter(recipe=recipe).exists()
        except Exception:
            return False

    is_favorited = SerializerMethodField(method_name='is_fav')
    is_in_shopping_cart = SerializerMethodField(method_name='is_in_cart')
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(many=False, read_only=True)
    # ingredients = IngredientRecipeSerializer(many=True, read_only=False)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            # "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField(
    #     default=serializers.CurrentUserDefault()
    # )
    # name = serializers.StringRelatedField(
    #     read_only = True
    # )

    class Meta:
        model = Recipe
        fields = (
            "name",


        )


class SubscriptionSerializer(serializers.Serializer):
    author = CustomUserSerializer().data

    class Meta:
        model = Subscription
        fields = (
            "author"
        )

    # def get_author(self, obj):
    #     print()
    #     return CustomUserSerializer().data
