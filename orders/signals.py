from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=Order)
def order_status_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()

    if instance.user:
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.user.id}",
            {
                "type": "order_status",
                "message": {
                    "order_id": instance.id,
                    "status": instance.status,
                    "status_pay": instance.status_pay,
                    "order_type": instance.order_type,
                }
            }
        )

    if instance.status == 'new':
        async_to_sync(channel_layer.group_send)(
            "new_orders",
            {
                "type": "new_order",
                "message": {
                    "order_id": instance.id,
                    "status": instance.status,
                    "user": instance.user.full_name if instance.user else 'Anonymous',
                    "total_price": instance.full_price,
                    "created_at": instance.created_at.isoformat(),
                }
            }
        )
