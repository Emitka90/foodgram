from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import pyshorteners
from django.http import HttpResponse

from .models import Tag, Recipe, Ingredient, Favorite, Shopping_cart, RecipeIngredients
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, ShortRecipeSerializer
#, RecipeMainSerializer, RecipeCreateSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

#class RecipieView(viewsets.ModelViewSet):
#    queryset = Recipe.objects.all()
#    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
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
#            favorite, context={'request': request}
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
#            .replace('/api', '')
            .replace('/get-link', '')
        )
        return Response({'short-link': short_url})
    

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
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
#            favorite, context={'request': request}
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
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

#    def get_serializer_class(self):
#        if self.action == 'create':
#            return RecipeCreateSerializer
#        return RecipeMainSerializer
