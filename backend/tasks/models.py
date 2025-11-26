from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hours = models.IntegerField()
    importance = models.IntegerField()
    dependencies = models.CharField(max_length=500, blank=True, default='')
    priority_score = models.FloatField(default=0.0)

    def __str__(self):
        return self.title
