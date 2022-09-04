# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models

SystemChoices = [('3.5e', 'D&D 3.5e'),
                 ('PF', 'Pathfinder'),
                 ('4e', 'D&D 4e'),
                 ('5e', 'D&D 5e'),
                 ('6e', 'D&D 6e Playtest')]


class GameRequest(models.Model):
    class Meta:
        unique_together = ['UserID', 'System']

    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    RequestName = models.CharField(max_length=200)
    System = models.CharField(max_length=200, choices=SystemChoices)
    CanDM = models.BooleanField(default=1)
    TravelRange = models.IntegerField(default=False)
    Address = models.CharField(max_length=200)
    City = models.CharField(max_length=100)
    State = models.CharField(max_length=100)
    ZIP = models.CharField(max_length=100)
    GISPoint = models.PointField(blank=True, null=True, srid=4326, spatial_index=False)

    def __str__(self):
        return self.RequestName


class Test(models.Model):
    Data = models.CharField(max_length=200)
