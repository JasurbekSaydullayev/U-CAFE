# Generated by Django 5.0.6 on 2024-06-20 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_order_lift'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='full_price',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='basket',
            name='position',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
