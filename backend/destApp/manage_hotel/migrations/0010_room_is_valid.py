# Generated by Django 4.1 on 2024-05-20 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_hotel', '0009_alter_booking_booking_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='is_valid',
            field=models.BooleanField(default=True),
        ),
    ]
