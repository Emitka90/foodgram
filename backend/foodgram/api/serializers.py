from rest_framework import serializers
from django.shortcuts import get_object_or_404

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredients,
    Favorite,
    Shopping_cart
)
import base64
from django.core.files.base import ContentFile
from users.serializers import UserReadSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
    )

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
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipe_ingredient'
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=True, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'cooking_time',
            'tags',
            'ingredients',
            'image',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def validate(self, data):
        if not self.initial_data.get("tags"):
            raise serializers.ValidationError(
                "Отсутствует поле 'tags'"
            )
        tags = self.initial_data.get("tags")
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError(
                    "Указан несуществующий тег"
                )
        if not tags:
            raise serializers.ValidationError(
                "Убедитесь, что добавлен хотя бы один тег"
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Теги должны быть уникальными")
        data["tags"] = tags
        ingredients = self.initial_data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "В рецепте отсутсвуют ингредиенты"}
            )
        ingredients_result = []
        ingredients_obj = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           pk=ingredient_item["id"]
                                           )
            if ingredient in ingredients_obj:
                raise serializers.ValidationError(
                    "Ингредиент уже добавлен в рецепт"
                )
            ingredients_obj.append(ingredient)
            amount = ingredient_item["amount"]
            if not (isinstance(ingredient_item["amount"], int)
                    or ingredient_item["amount"].isdigit()):
                raise serializers.ValidationError(
                    "Неправильное количество ингридиента"
                )
            ingredients_result.append(
                {
                    "id": ingredient,
                    "amount": amount
                }
            )
        data["recipe_ingredient"] = ingredients_result
        return data

    def get_is_in_shopping_cart(self, obj):
        if (
            self.context.get('request')
            and not self.context['request'].user.is_anonymous
        ):
            return Shopping_cart.objects.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        return False

    def get_is_favorited(self, obj):
        if (
            self.context.get('request')
            and not self.context['request'].user.is_anonymous
        ):
            return Favorite.objects.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        return False

    def create(self, validated_data):
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
