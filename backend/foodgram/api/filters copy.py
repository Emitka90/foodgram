import django_filters as filters

from .models import Recipe, Tag, Ingredient


class RecipeFilter(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.CharFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.CharFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorited", "is_in_shopping_cart"]

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorite__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart__user=user)
        return Recipe.objects.all()

class IngredientSearch(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', field_name='name')

    class Meta:
        model = Ingredient
        fields = ('name',)