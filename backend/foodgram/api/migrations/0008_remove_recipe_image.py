# Generated by Django 4.2.17 on 2024-12-21 19:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_rename_ingredient_recipe_ingredients_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='image',
        ),
    ]
