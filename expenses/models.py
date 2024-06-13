from django.db import models
from django.utils import timezone


class Expenses(models.Model):
    description = models.TextField()
    date = models.DateField(default=timezone.now)
    price = models.PositiveBigIntegerField()

    def __str__(self):
        return self.date
