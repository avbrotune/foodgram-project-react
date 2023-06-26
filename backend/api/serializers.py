import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeMiniSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


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
        request = self.context['request']
        return (request
                and request.user.is_authenticated
                and request.user.subscriber.filter(
                    author=instance
                ).exists())

    is_subscribed = SerializerMethodField(method_name='is_sub')

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
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
        read_only_fields = ("__all__",)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        read_only_fields = ("__all__",)


class IngredientRecipeSerializer(serializers.ModelSerializer):

    def get_ingredient_id(self, instance):
        return instance.ingredient.id

    def get_ingredient_name(self, instance):
        return instance.ingredient.name

    def get_ingredient_measurement_unit(self, instance):
        return instance.ingredient.measurement_unit

    id = serializers.SerializerMethodField(method_name="get_ingredient_id")
    name = serializers.SerializerMethodField(method_name="get_ingredient_name")
    measurement_unit = serializers.SerializerMethodField(
        method_name="get_ingredient_measurement_unit")

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class IngredientRecipeMiniSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), many=False)

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "amount",
        )


class RecipeSerializer(serializers.ModelSerializer):

    def is_fav(self, instance):
        user = self.context['request'].user
        recipe = instance.id
        return user.favorites.filter(recipe=recipe).exists()

    def is_in_cart(self, instance):
        user = self.context['request'].user
        recipe = instance.id
        return user.shopping_carts.filter(recipe=recipe).exists()

    def get_ingredients_with_amount(self, instance):
        '''
        Функция для получения ингредиента и его количества,
        но без вложенности.
        '''
        recipe = instance.id
        queryset = IngredientRecipe.objects.filter(recipe=recipe)
        return IngredientRecipeSerializer(queryset, many=True).data

    is_favorited = SerializerMethodField(method_name='is_fav')
    is_in_shopping_cart = SerializerMethodField(method_name='is_in_cart')
    tags = TagSerializer(many=True, required=True)
    author = CustomUserSerializer(many=False, read_only=True)
    ingredients = SerializerMethodField(
        method_name="get_ingredients_with_amount")
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeCreatePatchSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientRecipeMiniSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, data):
        for ingredient in data:
            if ("id" not in ingredient.keys()
                    or "amount" not in ingredient.keys()):
                raise serializers.ValidationError(
                    'Неверно указан игредиент.'
                )
        return data

    @staticmethod
    def create(validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        ingredients_in_recipe = []
        for ingredient in ingredients:
            ingredients_in_recipe.append(
                IngredientRecipe(
                    ingredient=ingredient["id"],
                    recipe=instance,
                    amount=ingredient["amount"]
                )
            )

        IngredientRecipe.objects.bulk_create(
            ingredients_in_recipe
        )
        for tag in tags:
            instance.tags.add(tag)
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        if validated_data.get('ingredients'):
            IngredientRecipe.objects.filter(recipe=instance).delete()
            ingredients = validated_data.get('ingredients')
            for ingredient in ingredients:
                IngredientRecipe.objects.create(
                    ingredient=ingredient["id"],
                    recipe=instance, amount=ingredient["amount"])
        if validated_data.get('tags'):
            instance.tags.clear()
            tags = validated_data.get('tags')
            for tag in tags:
                instance.tags.add(tag)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class SubscriptionSerializer(UserSerializer):

    def is_sub(self, instance):
        user = self.context['request'].user
        author = instance.id
        return user.subscriber.filter(author=author).exists()

    def rec_count(self, instance):
        return Recipe.objects.filter(author=instance.id).count()

    def recipe_limit(self, instance):
        limit = self.context['request'].query_params.get('recipes_limit', None)
        recipes = Recipe.objects.filter(author=instance.id)
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeMiniSerializer(recipes, many=True).data

    is_subscribed = SerializerMethodField(method_name='is_sub')
    recipes = SerializerMethodField(method_name='recipe_limit')
    recipes_count = SerializerMethodField(method_name='rec_count')

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "id",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count"
        )
