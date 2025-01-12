from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Tag, Ingredient, Recipe, RecipeIngredients
import base64
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
#        source='recipe_ingredient',
#        read_only=True
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'measurement_unit',
            'amount',
            'name'
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True, source='recipe_ingredient')
    tags = serializers.SlugRelatedField(
        many=True, queryset=Tag.objects.all(), slug_field="id"
    )
    image = Base64ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'text',
            'cooking_time',
            'tags',
            'ingredients',
            'image'
        )
    
    def create(self, validated_data):
        print(validated_data)
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipe_ingredient')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        recipe.tags.set(tags_data)
        print(recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipe_ingredient')
        RecipeIngredients.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()
        ).delete()
        for ingredient in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.tags.set(tags_data)
        instance.save()
        return instance

