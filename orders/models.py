from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from foods.models import Food
from users.models import User

import requests

pay_type = (
    ('cash', 'cash'),
    ('payme', 'payme'),
    ('click', 'click'),
    ('terminal', 'terminal'),
)

order_type = (
    ('delivery', 'delivery'),
    ('with', 'with'),
    ('there', 'there'),
)

status_choices = (
    ('new', 'New'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
)

status_pay_choices = (
    ('paid', 'Paid'),
    ('unpaid', 'Unpaid'),
)

delivery_choices = (
    ('waiting', 'Waiting'),
    ('on_road', 'On road'),
    ('delivered', 'Delivered'),
)

lift_choice = (
    ('right', 'Right'),
    ('left', 'Left'),
)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pay_type = models.CharField(max_length=50, choices=pay_type, default='cash')
    order_type = models.CharField(max_length=50, choices=order_type, default='there')
    position = models.IntegerField(default=1)
    full_price = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=50, choices=status_choices, default='new')
    status_pay = models.CharField(max_length=50, choices=status_pay_choices, default='unpaid')
    delivery_status = models.CharField(max_length=50, choices=delivery_choices, default='waiting', null=True,
                                       blank=True)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)
    lift = models.CharField(max_length=50, choices=lift_choice, default='left')
    webhook_url = models.URLField(blank=True, null=True)

    def calculate_order_price(self):
        total_price = 0
        for item in self.items.all():
            total_price += item.price
        return total_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(default=1)
    price = models.PositiveBigIntegerField()
