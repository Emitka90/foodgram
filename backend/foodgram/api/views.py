from rest_framework import viewsets 

from .models import Tag, Recipe, Ingredient
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer
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

#    def get_serializer_class(self):
#        if self.action == 'create':
#            return RecipeCreateSerializer
#        return RecipeMainSerializer
