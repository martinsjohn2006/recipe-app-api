"""
Serializers for the recipe API
"""
from rest_framework import serializers

from db_connection.models import Recipe, Tag

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link"]
        read_only_fields = ["id"]

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detial view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]

class TagSerializer(serializers.ModelSerializer):
    """Serializer for the tag model"""

    class Meta:
        model = Tag
        fields= ["id", "name"]
        read_only_fields = ["id"]