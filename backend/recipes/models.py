from colorfield.fields import ColorField
from django.core.validators import (
    MaxValueValidator, MinValueValidator)
from django.db import models

from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=200,
        unique=True
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name="Текст рецепта",
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientRecipe',
        blank=False,
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги',
        blank=False,
        related_name="recipes"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное значение 1'
            ),
            MaxValueValidator(
                10000,
                message='Максимальное значение 10000'
            ),
        ],
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}, автор - {self.author}"

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200,
    )

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
    )
    color = ColorField(default='#FF0000')
    # color = models.CharField(
    #     max_length=7,
    #     unique=True,
    #     validators=[RegexValidator(
    #         regex='^#[0-9a-fA-F]{6}',
    #         message='Введите HEX цвет в формате #xxxxxx'
    #     )],
    # )
    slug = models.CharField(
        max_length=200,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_amounts'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_amounts'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное значение 1'
            ),
            MaxValueValidator(
                10000,
                message='Максимальное значение 10000'
            ),
        ],
    )

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.name}'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    def __str__(self):
        return self.author.username

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='uniq_sub'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class CommonCartFavorite(models.Model):

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='uniq_%(class)s'
            ),
        )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )


class ShoppingCart(CommonCartFavorite):

    class Meta(CommonCartFavorite.Meta):
        default_related_name = "shopping_carts"
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return self.recipe.name


class Favorite(CommonCartFavorite):

    class Meta(CommonCartFavorite.Meta):
        default_related_name = "favorites"
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f"User: {self.user.username} \
            Recipe: {self.recipe.name}"
