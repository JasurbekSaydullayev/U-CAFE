# Generated by Django 5.0.6 on 2024-06-11 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('phone_number', models.CharField(blank=True, max_length=13, null=True)),
                ('description', models.TextField()),
            ],
        ),
    ]