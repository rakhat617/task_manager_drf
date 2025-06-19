from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import APIException, MethodNotAllowed, PermissionDenied
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from users.serializers import UserSerializer


class UserViewSet(ViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(responses={200: UserSerializer(many=True)})
    def list(self, request: Request) -> Response:
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UserSerializer, responses={201: "User successfully created", 400: "Error", 409: "Conflict"})
    def create(self, request: Request) -> Response:
        s = UserSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            User.objects.create_user(**s.validated_data)
            return Response(
                data={"message": "success"}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                data={"error": str(e)}, status=status.HTTP_409_CONFLICT
            )