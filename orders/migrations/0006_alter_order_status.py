# Generated by Django 5.0.6 on 2024-06-11 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_order_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', 'New'), ('processing', 'Processing'), ('completed', 'Completed')], default='processing', max_length=50),
        ),
    ]
