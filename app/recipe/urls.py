"""
URL mappings for the recipe app
"""
from django.urls import path,include

from rest_framework.routers import DefaultRouter

from recipe import views 


router = DefaultRouter()  #using this Default router provided by django, the url endpoints for our django view set 
# would be auto created and match appropraitely without us needing to manually type out all urls.
router.register("recipes", views.RecipeViewSet)
router.register("tags", views.TagViewSet)

app_name = "recipe"

urlpatterns = [
    path("",include(router.urls)),
]
#Instead of writing 6-7 URL patterns for recipes, I’m letting DRF’s router create them automatically from my RecipeViewSet.