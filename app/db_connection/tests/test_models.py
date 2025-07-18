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