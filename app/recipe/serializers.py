"""
Serializers for the recipe API
"""
from rest_framework import serializers

from db_connection.models import Recipe, Tag ,Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the ingredient model"""
    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]
class TagSerializer(serializers.ModelSerializer):
    """Serializer for the tag model"""

    class Meta:
        model = Tag
        fields= ["id", "name"]
        read_only_fields = ["id"]

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""
    tags = TagSerializer(many=True, required=False) # this is simply making the field for 
    # tags when creating a recipe optional and also making it possible to have more than one tag
    ingredients = IngredientSerializer(many=True, required=False)
    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags", "ingredients"]
        read_only_fields = ["id"]
    
    def _get_or_create_tags(self, tags, recipe):  # this is just a helper method to avoid duplicted code fragments
        """Handle the getting or creating of tags as needed"""
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag, # this makes it future proof incase you need to add more fields in the future
            )
            recipe.tags.add(tag_obj)
    
    def _get_or_create_ingredients(self, ingredients, recipe):
        """helper function to handle the getting or creating of tag as needed. """
        auth_user = self.context["request"].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)


    def create(self, validated_data):
        """Create a recipe""" 
        tags = validated_data.pop("tags", []) 
        ingredients = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data): #the instance there is simply the instance in the model we are trying to update
        """Update recipe"""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detial view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description", "image"] 

class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploadding images to recipes."""

    class Meta:
        model = Recipe
        fields = ["id", "image"]
        extra_kwargs = {"image":{"required":"True"}}

        # the reason for creating a seperate serializer for the image field is due to the fact that
        # we only like to upload one particlar type of data to a particular endpoint.
