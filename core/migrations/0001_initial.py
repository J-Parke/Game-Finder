# Generated by Django 3.2.15 on 2022-09-04 07:45

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Data', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='GameRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=200)),
                ('System', models.CharField(max_length=200)),
                ('Address', models.CharField(max_length=200)),
                ('City', models.CharField(max_length=100)),
                ('State', models.CharField(max_length=100)),
                ('ZIP', models.CharField(max_length=100)),
                ('GISPoint', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('UserID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]