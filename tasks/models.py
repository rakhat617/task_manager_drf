from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Task(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В процессе"),
        ("done", "Выполнено"),
    ]

    user = models.ForeignKey(
        verbose_name="автор задачи",
        to=User, 
        on_delete=models.CASCADE, 
        related_name='user_tasks'
        )
    title = models.CharField(
        verbose_name="название задачи",
        max_length=30
    )
    description = models.TextField(
        verbose_name="описание задачи",
        blank=True
    )
    due_date = models.DateField(
        verbose_name="дедлайн задачи"
    )
    status = models.CharField(
        verbose_name="статус задачи",
        choices=STATUS_CHOICES,
        default="new"
    )

    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status != 'done'

    def __str__(self):
        return self.title
