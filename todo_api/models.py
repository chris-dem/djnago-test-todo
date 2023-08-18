from django.db import models
from django.utils.translation import gettext_lazy as text

# Create your models here.


class Todo(models.Model):
    class TodoStatus(models.TextChoices):
        """
        Todo status enumerable denoting whether a todo task was completed or not.
        Choice of enumerable allows for the addition of additional todo status such as ongoing.
        """

        NOT_COMPLETED = "F", text("Not completed")
        COMPLETED = "T", text("Completed")

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    timestamp_creation = models.DateField(auto_now_add=True, auto_now=False, blank=True)
    timestamp_updated = models.DateField(auto_now_add=False, auto_now=True, blank=True)
    status = models.CharField(
        max_length=1, choices=TodoStatus.choices, default=TodoStatus.NOT_COMPLETED
    )

    def __str__(self):
        return self.task
