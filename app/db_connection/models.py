"""Database models"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)

class UserManager(BaseUserManager):
    """Mnanager for users."""

    def create_user(self, email, password=None, **extra_field):
        """Create, save and return a new user."""

        if not email:
            raise ValueError("User mail must be set must be set.")
        user = self.model(email=email, **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name  = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UserManager() # this simple instantiate our custom user manager
    USERNAME_FIELD = "email" # this is us specifying that we want our username
    # to be the email the user inputs