# Generated by Django 4.1 on 2024-05-15 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_hotel', '0002_room_room_description_room_room_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_type',
            field=models.CharField(choices=[('Standard', 'Standard'), ('Single', 'Single'), ('Double', 'Double'), ('Deluxe', 'Deluxe')], default='standard', max_length=20),
        ),
    ]
