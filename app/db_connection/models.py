"""Database models"""

from django.conf import settings 
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)

class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_field):
        """Create, save and return a new user."""

        if not email:
            raise ValueError("User email must be set must be set.")
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password) #we set the password like this so that it would be hashed before saving 
        
        user.save(using=self._db)

        return user
    def create_superuser(self,email,password):
        """Create nad return new super user"""
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True

        user.save(using= self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name  = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UserManager() # this simply instantiate our custom user manager
    USERNAME_FIELD = "email" # this is us specifying that we want our username
    # to be the email the user inputs

class Recipe(models.Model):
    """Recipe project"""
    user  = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True) 
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title 