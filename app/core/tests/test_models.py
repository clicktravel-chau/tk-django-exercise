from django.test import TestCase

from core import models


class ModelTests(TestCase):

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            name='Cucumber',
            recipe=models.Recipe.objects.create(
                name='Cucumber pie',
                description='What is this?',
            ),
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            name='Steak and mushroom sauce',
            description='Some type of gravy',
        )

        self.assertEqual(str(recipe), recipe.name)
