# Generated by Django 3.2.15 on 2022-09-05 05:52

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_gamerequest_gispoint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamerequest',
            name='CanDM',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gamerequest',
            name='GISPoint',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, default=django.contrib.gis.geos.point.Point([]), null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='gamerequest',
            name='TravelRange',
            field=models.IntegerField(default=1),
        ),
    ]
