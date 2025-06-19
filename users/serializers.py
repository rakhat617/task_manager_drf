from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=50)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    def validate_username(self, value):
        if "admin" in value.lower():
            raise serializers.ValidationError("Username cannot contain 'admin'")
        return value

    def validate(self, attrs):
        if attrs["username"] == attrs.get("password"):
            raise serializers.ValidationError("Password cannot be the same as username")
        self.validate_username(value=attrs["username"])
        return attrs

    def create(self, validated_data):
        validated_data["password"] = make_password(
            validated_data["password"]
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"]
            )
        return super().update(instance, validated_data)