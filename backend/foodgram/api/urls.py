from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import TagViewSet, IngredientViewSet, RecipeViewSet, download_shopping_cart

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
    path(
        "recipes/download_shopping_cart/",
        download_shopping_cart,
        name="download",
    ),
    path('', include(router.urls)),
] 