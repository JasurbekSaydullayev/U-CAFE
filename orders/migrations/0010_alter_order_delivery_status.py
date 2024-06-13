# Generated by Django 5.0.6 on 2024-06-13 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_order_delivery_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_status',
            field=models.CharField(blank=True, choices=[('waiting', 'Waiting'), ('on_road', 'On road'), ('delivered', 'Delivered')], default='waiting', max_length=50, null=True),
        ),
    ]
