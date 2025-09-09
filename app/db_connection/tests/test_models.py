"""
Tests for models.
"""

from unittest.mock import patch
from decimal import Decimal 

from django.test import TestCase
from django.contrib.auth import get_user_model

from db_connection import models

def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email,password)

class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        "Test if user email and password was created succesfully"
        email = "test@example.com"
        password = "testpass123"

        user = get_user_model().objects.create_user(
            email= email,
            password= password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password)) #the check_password method 
        # allows us to check if the user password is the sane as the hashed password

    def test_new_user_normalised(self):
        """Test email is normalised for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com","test1@example.com"],
            ["Test2@EXAMPLE.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"]
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email,"sample123")
            self.assertEqual(user.email, expected)
    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user("", "sample123")
    def test_create_superuser(self):
        """Test to create super user"""
        user = get_user_model().objects.create_superuser(
            "test@example.come",
            "test123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_create_recipe(self):
        """Test creating a recipe is successful """
        user = get_user_model().objects.create_user(
            "test@example.com"
            "testpass123",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name", 
            time_minutes=5,
            price=Decimal("5.50"), 
            description="Simple recipe description",
        )

        self.assertEqual(str(recipe), recipe.title)
    
    def test_create_tag(self):
        """Test creating tag is successful and that the __str__ method in the model works"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag),tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful and that the __str__ method in the model works"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient1"
        )

        self.assertEqual(str(ingredient), ingredient.name)   
    @patch("db_connection.models.uuid.uuid4")  # freeze randomness so test is reproducible.
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating unique image file path"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")