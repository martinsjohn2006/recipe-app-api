"""
Url routes for the User app
"""
from django.urls import path
from .views import *

app_name = "user" #this would be used by the reverse, mapping in the test script.

urlpatterns = [
    path("create/",CreateUserView.as_view(), name="create"),
    path("token/", CreateTokenView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="me"),
    
]
