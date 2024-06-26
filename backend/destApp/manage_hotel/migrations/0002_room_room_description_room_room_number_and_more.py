# Generated by Django 4.1 on 2024-05-15 09:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manage_hotel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='room_description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='room_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='room_type',
            field=models.CharField(choices=[('standard', 'Standard'), ('single', 'Single'), ('double', 'Double'), ('deluxe', 'Deluxe')], default='standard', max_length=20),
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_time', models.DateTimeField()),
                ('start_time', models.DateField()),
                ('end_time', models.DateField()),
                ('check_in', models.DateField(blank=True, null=True)),
                ('check_out', models.DateField(blank=True, null=True)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manage_hotel.room')),
            ],
        ),
    ]
