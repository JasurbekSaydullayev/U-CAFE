from django.contrib.auth.models import AbstractUser
from django.db import models

user_type = (
    ('Admin', 'Admin'),
    ('Manager', 'Manager'),
    ('Cook', 'Cook'),
    ('Seller', 'Seller'),
    ('Courier', 'Courier'),
    ('Barmen', 'Barmen'),
    ('Waitress', 'Waitress'),
    ('Customer', 'Customer'),
)


class User(AbstractUser):
    user_type = models.CharField(max_length=20, choices=user_type, default='Customer')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    salary = models.PositiveBigIntegerField(null=True)
    image = models.ImageField(upload_to='users', null=True, blank=True)

    def __str__(self):
        return self.username
