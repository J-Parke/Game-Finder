# Generated by Django 3.2.15 on 2022-09-11 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20220911_0533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamerequest',
            name='available_dms',
            field=models.ManyToManyField(blank=True, default=None, to='core.GameRequest'),
        ),
    ]
