"""
Views for the recipe API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from db_connection.models import Recipe 
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipe for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-id") # accessing the user data inside the request
        #we are doing this because we know that the authenticated user would be 
        #passed back to us by the authentication system.
    
    def get_serializer_class(self):
        """Return the serializer class for request """
        if self.action == "list":
            return serializers.RecipeSerializer

        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)
       # this would save the currently authenticated user alongside the recipe being saved 
       # reasin why we are doing this is due to the fact that we have a relation that is user 
       # between the user and recipe model.
       # we are creating a way to get to set the user id on the server side instead of the client having 
        # to send it, we do not want that, if we do not do it, when we try to save a recipe, it would tell 
        # us that the data column is null