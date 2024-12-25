from rest_framework import serializers

from .models import Tag, Ingredient, Recipe, RecipeIngredients


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'ingredient',
            'recipe',
            'amount',
        )


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
#    id = serializers.PrimaryKeyRelatedField(
#        queryset=Ingredient.objects.all()
#    )
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientToRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField()
    tags = serializers.SlugRelatedField(
        many=True, queryset=Tag.objects.all(), slug_field="id"
    )
    id = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'tags', 'name', 'text',
                  'cooking_time', 'author')


    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients_data:
#            amount=ingredient.pop('amount'),
            current_ingredient = Ingredient.objects.get(pk=ingredient['id'])
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
#                amount=ingredient.pop('amount'),
                amount=amount
            )
        recipe.tags.set(tags_data)
        return recipe


class RecipeMainSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True)
    tags = TagSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'text',
            'cooking_time',
            'tags',
            'ingredients',
        )
    
#    def create(self, validated_data):
#        tags_data = validated_data.pop('tags')
#        ingredients_data = validated_data.pop('ingredients')
#        recipe = Recipe.objects.create(**validated_data)

#        for ingredient in ingredients_data:
#            current_ingredient = Ingredient.objects.get(id=ingredient)
#            RecipeIngredients.objects.create(
#                recipe=recipe,
#                ingredient=current_ingredient,
#                amount=ingredient.get("amount"),
#            )

#        for ingredient in ingredients_data:
#            RecipeIngredients.objects.create(
#                recipe=recipe,
#                ingredient=ingredient['id'],
#                amount=ingredient['amount']
#            )
#        recipe.tags.set(tags_data)
#        return recipe
