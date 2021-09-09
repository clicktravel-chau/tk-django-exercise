from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return the recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_ingredient(recipe, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(name=name, recipe=recipe)


def sample_recipe(**params):
    """Create and return a sample recipe"""
    defaults = {
        'name': 'Sample recipe',
        'description': 'this is a description'
    }
    defaults.update(params)

    return Recipe.objects.create(**defaults)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        recipe1 = sample_recipe(name='Apple strudel', description='123')
        recipe2 = sample_recipe(name='Rhubarb pie', description='456')

        res = self.client.get(RECIPES_URL)

        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe2.name, res.data[0]['name'])
        self.assertEqual(recipe2.description, res.data[0]['description'])
        self.assertEqual(recipe1.name, res.data[1]['name'])
        self.assertEqual(recipe1.description, res.data[1]['description'])

    def test_retrive_recipes_by_name(self):
        """Test retrieving a list of recipes filtered by name"""
        recipe = sample_recipe(name='Pizza')
        sample_recipe(name='Spaghetti bolognese')

        res = self.client.get(
            RECIPES_URL,
            {'name': 'Pi'}
        )

        serializer = RecipeSerializer(recipe)
        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer.data, res.data)

    def test_view_recipe_details(self):
        """Test viewing the recipe detail"""
        recipe = sample_recipe()
        recipe.ingredients.add(sample_ingredient(recipe=recipe))

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ingredient1 = {'name': 'Prawns'}
        ingredient2 = {'name': 'Ginger'}
        payload = {
            'name': 'Thai prawn red curry',
            'ingredients': [ingredient1, ingredient2],
            'description': 'Nice and spicy!'
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertTrue(ingredients
                        .filter(name=ingredient1["name"])
                        .exists())
        self.assertTrue(ingredients
                        .filter(name=ingredient2["name"])
                        .exists())

    def test_partial_update_recipe(self):
        """Test updating a recipe with PATCH"""
        recipe = sample_recipe()
        recipe.ingredients.add(sample_ingredient(recipe=recipe))
        new_ingredient = {'name': 'Curry powder'}

        payload = {
            'name': 'Chicken tikka',
            'ingredients': [new_ingredient],
            'description': 'testing'
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload, format='json')

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 1)
        self.assertTrue(ingredients
                        .filter(name=new_ingredient["name"])
                        .exists())

    def test_full_update_recipe(self):
        """Test updating a recipe with PUT"""
        recipe = sample_recipe()
        recipe.ingredients.add(sample_ingredient(recipe=recipe))
        payload = {
            'name': 'Spaghetti carbonara',
            'description': 'A very nice pasta dish',
            'ingredients': [{'name': 'Beef bacon'}, {'name': 'Black peppers'}]
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload, format='json')

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)

    def test_delete_recipe(self):
        """Test deleing a recipe with given ID"""
        recipe = sample_recipe()
        recipe.ingredients.add(sample_ingredient(recipe=recipe))

        url = detail_url(recipe.id)
        self.client.delete(url)

        recipes = Recipe.objects.all()
        ingredients = Ingredient.objects.all()
        self.assertEqual(recipes.count(), 0)
        self.assertEqual(ingredients.count(), 0)
