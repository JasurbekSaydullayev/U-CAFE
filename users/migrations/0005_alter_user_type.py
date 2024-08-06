# Generated by Django 5.0.6 on 2024-08-05 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('Admin', 'Admin'), ('Manager', 'Manager'), ('Cook', 'Cook'), ('Cashier', 'Cashier'), ('Courier', 'Courier'), ('Barmen', 'Barmen'), ('Waitress', 'Waitress'), ('Customer', 'Customer')], default='Customer', max_length=20),
        ),
    ]