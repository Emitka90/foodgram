from api.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                        Shopping_cart, Tag)
from django.contrib import admin


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    empty_value_display = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = "-пусто-"


class RecipeIngredientInline(admin.TabularInline):
    """
    Для отображения в админке поля ManyToMany ингредиентов в рецепте c through.
    """
    model = RecipeIngredients
    min_num = 1
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('author', 'name', 'favorite_count')
    list_filter = ('author', 'name', 'tags')
    empty_value_display = "-пусто-"

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    empty_value_display = "-пусто-"


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = "-пусто-"


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = "-пусто-"


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteRecipeAdmin)
admin.site.register(Shopping_cart, ShoppingCartAdmin)
