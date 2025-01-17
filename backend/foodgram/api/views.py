import pyshorteners
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientSearch, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     Shopping_cart, Tag)
from .pagination import LimitPageNumberPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get', 'head', 'options']
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get', 'head', 'options']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearch
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["post"], detail=True, permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response({
                'errors': 'Уже в избранном'
            }, status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(
            recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path='get-link')
    def get_short_link(self, request, pk):
        shortener = pyshorteners.Shortener()
        short_url = shortener.tinyurl.short(
            request.build_absolute_uri()
            .replace('/get-link', '')
        )
        return Response({'short-link': short_url})

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if Shopping_cart.objects.filter(user=user, recipe=recipe).exists():
            return Response({
                'errors': 'Уже в списке покупок.'
            }, status=status.HTTP_400_BAD_REQUEST)

        Shopping_cart.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(
            recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def del_recipe_shoping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shoping_cart = Shopping_cart.objects.filter(user=user, recipe=recipe)
        if shoping_cart.exists():
            shoping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def download_shopping_cart(request):
    user = request.user
    shopping_cart = user.shopping_cart.all()
    shopping_list = {}
    for record in shopping_cart:
        recipe = record.recipe
        ingredients = RecipeIngredients.objects.filter(recipe=recipe)
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in shopping_list:
                shopping_list[name] = {
                    "measurement_unit": measurement_unit,
                    "amount": amount,
                }
            else:
                shopping_list[name]["amount"] = (
                    shopping_list[name]["amount"] + amount
                )
    content = []
    for name, data in shopping_list.items():
        content.append(
            f"{name} - {data['amount']} {data['measurement_unit']}\n"
        )
    filename = "shoping_cart.txt"
    response = HttpResponse(content, content_type="text/plain")
    response['Content-Disposition'] = (
        'attachment; filename={0}'.format(filename)
    )
    return response
