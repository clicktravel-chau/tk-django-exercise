from rest_framework import serializers

from core.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'ingredients', 'description'
        )
        depth = 1
        read_only_fields = ('id',)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients_data:
            Ingredient.objects.create(**ingredient, recipe=recipe)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()

        Ingredient.objects.filter(recipe_id=self.instance.id).delete()

        recipe = Recipe.objects.get(id=self.instance.id)
        for ingredient in ingredients_data:
            Ingredient.objects.create(**ingredient, recipe=recipe)

        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail"""
    ingredients = IngredientSerializer(many=True, read_only=True)
