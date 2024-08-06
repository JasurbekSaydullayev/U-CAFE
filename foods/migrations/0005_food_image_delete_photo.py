# Generated by Django 5.0.6 on 2024-07-29 04:08

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0004_alter_food_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='image',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='photos'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Photo',
        ),
    ]