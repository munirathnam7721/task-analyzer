from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    priority_score = serializers.FloatField(read_only=True)
    explanation = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance', 'dependencies', 'priority_score', 'explanation']
