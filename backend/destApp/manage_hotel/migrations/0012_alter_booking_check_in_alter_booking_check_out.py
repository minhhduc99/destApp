# Generated by Django 4.1 on 2024-05-20 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_hotel', '0011_booking_booking_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='check_in',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='check_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
