from django.contrib.auth.models import AbstractUser
from django.db import models

user_type = (
    ('Admin', 'Admin'),
    ('Manager', 'Manager'),
    ('Cook', 'Cook'),
    ('Cashier', 'Cashier'),
    ('Courier', 'Courier'),
    ('Barmen', 'Barmen'),
    ('Waitress', 'Waitress'),
    ('Customer', 'Customer'),
)


class User(AbstractUser):
    type = models.CharField(max_length=20, choices=user_type, default='Customer')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    salary = models.PositiveBigIntegerField(null=True)

    def __str__(self):
        return self.username
