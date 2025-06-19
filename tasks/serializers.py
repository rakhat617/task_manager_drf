from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from tasks.models import Task
from users.serializers import UserSerializer



class TaskViewSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer()
    title = serializers.CharField(max_length=30)
    description = serializers.CharField(allow_blank=True)
    status = serializers.ChoiceField(choices=['new', 'in_progress', 'done'])
    due_date = serializers.DateField()
    is_overdue = serializers.BooleanField(read_only=True)
    

class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=30)
    description = serializers.CharField(allow_blank=True)
    status = serializers.ChoiceField(choices=['new', 'in_progress', 'done'])
    due_date = serializers.DateField()

    def create(self, validated_data: dict):
        user = self.context.get('user')
        if user is None:
            raise serializers.ValidationError("User not provided in context")
        validated_data["user"] = user
        task = Task.objects.create(**validated_data)
        return task

    def update(self, instance: Task, validated_data: dict):
        if instance.is_overdue:
            raise PermissionDenied(detail="this task is already overdue")
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.save()
        return instance