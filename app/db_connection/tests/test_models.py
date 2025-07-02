"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

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