from django.contrib import admin
# from django.utils.html import format_html
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

        return mark_safe('<img src="recipes/images/%s" \
                         width="130" height="100" />' % (obj.image.url))
        # return format_html('<img src="{}" style="width: 130px; \
        #                    height: 100px"/>'.format(obj.image.url))

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
