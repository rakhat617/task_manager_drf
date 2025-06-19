from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication

from tasks.models import Task
from tasks.serializers import TaskSerializer, TaskViewSerializer


class TaskViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in title", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by due_date or -due_date", type=openapi.TYPE_STRING),
        ],
        responses={
            200: TaskViewSerializer(many=True)
        }
    )
    def list(self, request: Request) -> Response:
        tasks: QuerySet[Task] = request.user.user_tasks.all()

        search_query = request.query_params.get('search')
        if search_query:
            tasks = tasks.filter(title__icontains=search_query)

        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)

        ordering = request.query_params.get('ordering')
        if ordering in ['due_date', '-due_date']:
            tasks = tasks.order_by(ordering)

        serializer = TaskViewSerializer(instance=tasks, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={
            201: TaskSerializer,
            400: "bad request"
        }
    )
    def create(self, request: Request) -> Response:
        serializer = TaskSerializer(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        response_serializer = TaskViewSerializer(instance=task)
        return Response(data=response_serializer.data)

    @swagger_auto_schema(
        responses={
            200: TaskViewSerializer,
            404: "task does not exist"
        }
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        try:
            task: Task = request.user.user_tasks.get(pk=pk)
        except Task.DoesNotExist:
            return Response(
                data="task does not exist",
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TaskViewSerializer(instance=task)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={
            200: "task updated",
            403: "forbidden",
            404: "bad request"
        }
    )
    def update(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, pk=pk)
        if task.user != request.user:
            raise PermissionDenied(detail="forbidden, not your task")
        serializer = TaskSerializer(instance=task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data="task updated", status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={
            200: "task updated",
            403: "forbidden",
            404: "bad request"
        }
    )
    def partial_update(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, pk=pk)
        if task.user != request.user:
            raise PermissionDenied(detail="forbidden, not your task")
        serializer = TaskSerializer(instance=task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data="task updated", status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            200: "task was removed",
            403: "forbidden",
            404: "task not found"
        }
    )
    def destroy(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, pk=pk)
        if task.user != request.user:
            raise PermissionDenied(detail="forbidden, not your task")
        task.delete()
        return Response(data="task was removed", status=status.HTTP_200_OK)