from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from foods.models import Food
from users.models import User

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
    ('processing', 'Processing'),
    ('delivering', 'Delivering'),
    ('completed', 'Completed'),
)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    pay_type = models.CharField(max_length=50, choices=pay_type, default='cash')
    order_type = models.CharField(max_length=50, choices=order_type, default='there')
    position = models.IntegerField(default=1)
    full_price = models.PositiveBigIntegerField()
    status = models.CharField(max_length=50, choices=status_choices, default='processing')
    delivery_address = models.CharField(max_length=255, blank=True, null=True)

    def calculate_order_price(self):
        total_price = 0
        for item in self.items.all():
            total_price += item.price * item.quantity
        return total_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(default=1)
    price = models.PositiveBigIntegerField()


@receiver(post_save, sender=OrderItem)
def update_order_on_order_item_save(sender, instance, created, **kwargs):
    if created:
        instance.order.position = instance.order.items.count()
        instance.order.full_price = instance.order.calculate_order_price()
        instance.order.save()
