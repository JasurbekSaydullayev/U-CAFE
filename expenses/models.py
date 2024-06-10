from django.db import models


class Expenses(models.Model):
    description = models.TextField()
    date = models.DateField()
    price = models.PositiveBigIntegerField()

    def __str__(self):
        return self.date
