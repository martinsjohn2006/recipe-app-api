"""Database models"""
import os 
import uuid
from django.conf import settings 
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)

def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = os.path.splitext(filename)[1] # this gives us the file extension
    # we use the uuid to generate a unique
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads","recipe", filename) # the reason why we are using the join and splittext functions 
# from the os module is to ensure that our code works on all operating systems

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
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path) 

    def __str__(self):
        return self.title 

class Tag(models.Model):
    """Tag for filtering recipes"""
    name = models.CharField(max_length=225)
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    """Ingredient for recipes. """
    name = models.CharField(max_length=225)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, )
    
    def __str__(self):
        return self.name