# Generated by Django 5.0.6 on 2024-08-08 08:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_user_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='type',
            new_name='user_type',
        ),
    ]
