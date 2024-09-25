# serializers.py
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id','name', 'description', 'qualification', 'due_date', 'created_by']
        read_only_fields = ['created_by']  # Ensure 'created_by' is read-only when creating
