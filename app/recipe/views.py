"""
Views for the recipe API
"""
from django.db.models import query
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,)
from rest_framework import (
    viewsets,
    mixins,
    status)
from rest_framework.decorators import action
from rest_framework.response import Response 
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from db_connection.models import Recipe, Tag, Ingredient  
from recipe import serializers

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "assigned_only", 
                OpenApiTypes.INT, enum=[0,1],
                description="filter by items assigned to recipe."
            )
        ]
    )
)
class BaseRecipeAttr(mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    """Base class for inheritance for the TagViewSet and RecipeViewset"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """filter the queryset to only include that of the authenticated user making the request"""
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", 0))  # defualt value to be returned in there is nothing assigned to "assigned_only"
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        
        return queryset.filter(
            user=self.request.user
            ).order_by("-name").distinct()

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="Comma separated list of tag IDs to filter",
            ), 
            OpenApiParameter(
                "ingredients", 
                OpenApiTypes.STR,
                description="Comma separated list of ingredient IDs to filter"
            )
        ]
    )
) # with this decorator, we are extending the list view schema functionality to support filtering by tags or ingredients 
# it really does not have any effect on the backend, it ony does to the OpenAPI schema
class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of string to integers."""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve recipe for authenticated user"""
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
             

# returning distinct values because one recipe can be assigned to more than one tag or ingredient.
        return queryset.filter(user=self.request.user).order_by("-id").distinct() 
       
    def get_serializer_class(self): # the way is that image uploads would be separate from uploading other fields. so as a post request
        """Return the serializer class for request """
        if self.action == "list":
            return serializers.RecipeSerializer
        
        elif self.action == "upload_image": # this is a custom action
            return serializers.RecipeImageSerializer

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

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

class TagViewSet(BaseRecipeAttr):
    """Manage tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
class IngredientViewSet(BaseRecipeAttr):
    """Manage ingredients in the database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    