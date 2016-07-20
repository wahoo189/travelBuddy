# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-18 23:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TravelBuddyApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip_join',
            name='owner',
        ),
        migrations.AddField(
            model_name='trip_join',
            name='attendee',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, related_name='attendee', to='TravelBuddyApp.Trip'),
        ),
        migrations.AddField(
            model_name='trip_join',
            name='tripOwner',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, related_name='tripOwner', to='TravelBuddyApp.Trip'),
        ),
    ]