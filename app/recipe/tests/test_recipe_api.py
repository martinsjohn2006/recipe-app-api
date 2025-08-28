"""Tests  for the recipe API"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status 
from rest_framework.test import APIClient

from db_connection.models import Recipe, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")

def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse("recipe:recipe-detail", args=[recipe_id])

def create_recipe(user, **params): 
    """Helper function for creating recipes."""
    defaults = {
        "title":"Simple recipe title",
        "time_minutes":22, 
        "price":Decimal(6.25),
        "description":"Sample description",
        "link": "https://example.com/recipe.pdf"
    }
    defaults.update(**params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)

class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API request"""
    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com",password="pass123")
        self.client.force_authenticate(self.user)

    def test_retreive_recipes(self):
        """test to retreive list of recipe for the use"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""
        other_user = create_user(
           email= "other@example.com",
            password="password123",
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes,many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
    
    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
    
    def test_creat_recipe(self):
        """Test creating a recipe through the api and not directly to the db"""
        payload = {
            "title":"Sample recipe",
            "time_minutes":30,
            "price": Decimal("5.99"),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value) # pay attention to the getattr() function.
        self.assertEqual(recipe.user, self.user) 
        # note that through out the above, the actual user was not associated to the response so we 
        #are not dealing with a User view but a model view, so we have to implement that logic in our
        # mode viewset so that our user object get sent alongsides our api response
    
    def test_partial_update(self):
        """Test partial update of a recipe"""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="sample recipe title",
            link=original_link,
        )
        payload = {"title": "New recipe title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)

    def test_full_update(self):
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link="https://example.com/recipe.pdf",
            description="sample recipe description"
        )
        payload = {
            "title":"New recipe title",
            "link":"https://example.com/new-recipe.pdf",
            "description":"New recipe description",
            "time_minutes":10,
            "price":Decimal("2.50")
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe,k), v)
        
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Testing deleting a recipe was successful."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another user reccipe yields an error"""
        new_user = create_user(email="othertestUser@gmail.com", password="newtestpass")
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res  = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def create_recipe_with_new_tag(self):
        """Test to create recipe with a new tag"""
        payload = {
            "title":"This is prawn curry",
            "time_minutes":20, 
            "price":Decimal(2.50),
            "tags":[{"name":"thai"}, {"name":"Dinner"}] # this is the rason why we need a nested serializer
        }

        res = self.client.post(RECIPES_URL,payload, format="json") # we have to state that 
        #despite the nested nature of the request, the required respose should still be json

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipes.tags.count(), 2) # the strange looking (recipes.tags.count()) is just db instance and stuff
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
                ).exists()
            
            self.assertTrue(exists)
    
    def test_create_recipe_with_existing_tags(self):
        """Test creating with existing tag."""

        tag_indian = Tag.objects.create(user=self.user, name="Indian")
        pay_load = {
            "title":"Pongal",
            "time_minutes":60, 
            "price": Decimal("4.5"),
            "tags": [{"name":"Indian"}, {"name":"Breakfast"}]
        }

        res = self.client.post(RECIPES_URL,pay_load, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in pay_load["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"], 
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_when_updating_recipe(self):
        """Test creating a tag when making a recipe update"""
        recipe = create_recipe(user=self.user)

        payload = {"tags":[{"name":"Lunch"}]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.filter(user=self.user, name="Lunch")
        self.assertIn(new_tag,recipe.tags.all())

    def test_update_recipe_with_already_existing_tag(self):
        """Test assigning an already existing tag when updating a recipe, and removes old tags if not in update"""
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        payload = {"tags":[{"name":"Lunch"}]} # to change the tag entirely not add, so no breakfast tag anymore 
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tag"""
        tag = Tag.objects.create(user=self.user, name="Desert")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload ={"tags":[]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload,format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.all(), 0)