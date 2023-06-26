from django.contrib import admin
from django.utils.safestring import mark_safe

from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Subscription, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ("image_tag", "name", "author", "show_favorite")
    list_filter = ("author", "name", "tags")

    @admin.display(description="Изображение блюда")
    def image_tag(self, obj):
        if obj.image:
            return mark_safe('<img src="{0}" width="130" \
                             height="130" style="object-fit:cover"\
                              />'.format(obj.image.url))
        else:
            return '(No image)'

    @admin.display(description="Добавлено в избранное, раз")
    def show_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    ...


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("name", )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    ...


@admin.register(Favorite)
class FavouriteAdmin(admin.ModelAdmin):
    ...


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    ...
