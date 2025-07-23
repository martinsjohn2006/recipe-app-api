"""
Serializer for the user API view 
"""
from django.contrib.auth import get_user_model,authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    "Serializer for User object"

    class Meta:
        model = get_user_model()
        fields = ["email","password","name"]
        extra_kwargs = {"password":{"write_only":True, "min_length": 5}}

    def create(self, validated_data): #this is actually overriding the inherited created method so that we 
        #can save the password and other data after it as been vaidated by the serializer
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    #have to override the already existing update method, so that we can hash the password while updating
    def update(self, validated_data):
        """Update and return user"""
        # pops out the password so that it does not get saved the normal way as other fields if password was not updated, default is None
        #then proceeds to store other fields, by calling the actual initial update method in the parent class
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data) 

        # hashes password and saves it.
        if password:
            user.set_password(password)
            user.save()
        
        return user 

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type":"password"},
        trim_whitespace=False, 
    )
    #validator method
    def validate(self,attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")

        #authenticate is an helper function that helps with looking up the credentials 
        #in user credentials in the database and acualy ensuring it exists.
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg,code="authorization")
        
        attrs["user"] = user # this adds the already validated user to the attrs dictionary.
        return attrs