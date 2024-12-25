# Generated by Django 4.2.17 on 2024-12-15 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_recipe_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredient',
            field=models.ManyToManyField(through='api.RecipeIngredients', to='api.ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipeingredients',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='api.ingredient'),
        ),
    ]
