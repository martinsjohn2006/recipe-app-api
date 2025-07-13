"""
Test for the admin modifications
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    """Test for Django admin."""

    def setUp(self): #this acts like your __int__ method to set variable instances, this is peculiar to django
        # it would run before any other method
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="user@example.com",
            password="testpass123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user1@example.com",
            password="testpass123",
            name="Test User"
        )
    def test_user_list(self):
        """Test that users are listed on page"""
        url = reverse("admin:db_connection_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works"""
        url = reverse("admin:db_connection_user_change", args = [self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works"""
        url = reverse("admin:db_connection_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)