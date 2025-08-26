from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ListPriority(models.TextChoices):
    LOW = "low", "low"
    MEDIUM = "medium", "medium"
    HIGH = "high", "high"


class ListStatus(models.TextChoices):
    NOT_STARTED = "not-started", "not-started"
    IN_PROGRESS = "in-progress", "in-progress"
    COMPLETED = "completed", "completed"


class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(
        max_length=6,
        choices=ListPriority.choices,
    )
    status = models.CharField(
        max_length=11,
        choices=ListStatus.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lists"


class TaskPriority(models.TextChoices):
    LOW = "low", "low"
    MEDIUM = "medium", "medium"
    HIGH = "high", "high"


class TaskStatus(models.TextChoices):
    NOT_STARTED = "not-started", "not-started"
    IN_PROGRESS = "in-progress", "in-progress"
    COMPLETED = "completed", "completed"


class Task(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(
        max_length=6,
        choices=TaskPriority.choices,
    )
    status = models.CharField(
        max_length=11,
        choices=TaskStatus.choices,
    )
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
