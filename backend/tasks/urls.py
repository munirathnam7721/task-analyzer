from django.urls import path
from .views import TaskAnalyzeView, TaskSuggestView

urlpatterns = [
    path('tasks/analyze/', TaskAnalyzeView.as_view(), name='task-analyze'),
    path('tasks/suggest/', TaskSuggestView.as_view(), name='task-suggest'),
]
