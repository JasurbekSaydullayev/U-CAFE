# # apps/chat/signals.py
#
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Order
# from .consumers import OrderStatusConsumer
#
#
# @receiver(post_save, sender=Order)
# def order_status_changed(sender, instance, created, **kwargs):
#     if not created:  # Если заказ не только что создан
#         OrderStatusConsumer.notify_order_status(instance.pk, instance.status)
