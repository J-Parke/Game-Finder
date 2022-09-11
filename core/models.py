# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.conf import settings

from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.dispatch import receiver
from core.functions import coordinates_from_api, fake_coordinates


import random

# Supported game systems. This must be a fixed set of choices to
# avoid having to accommodate different abbreviations (ex: 5e vs.
# 5th Edition).
# If the project scales to include a non-developer admin this should
# be converted to a model so it can be managed via the admin panel.
SYSTEMCHOICES = [('3.5e', 'D&D 3.5e'),
                 ('PF', 'Pathfinder'),
                 ('4e', 'D&D 4e'),
                 ('5e', 'D&D 5e'),
                 ('6e', 'D&D 6e Playtest')]


class GameRequest(models.Model):
    class Meta:
        unique_together = ['user_id', 'system']

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    request_name = models.CharField(max_length=200)
    system = models.CharField(max_length=200, choices=SYSTEMCHOICES)
    can_dm = models.BooleanField(default=False)
    available_dms = models.ManyToManyField("self", blank=True, default=None, symmetrical=False)
    travel_range = models.IntegerField(default=1)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    gis_point = models.PointField(blank=True, null=True, srid=4326, default=Point([]))

    def save(self, *args, **kwargs):
        update_fields = []

        if self.pk is not None and self.gis_point is not ():
            dms = GameRequest.objects.filter(gis_point__distance_lt=(self.gis_point, Distance(mi=self.travel_range))).filter(system=self.system).filter(can_dm=True)
            print(dms)
            for dm in dms:
                print(self.request_name + ' adding ' + dm.request_name)
                self.available_dms.add(dm)

        if self.pk is None:
            update_fields = ['user_id',
                             'request_name',
                             'system',
                             'can_dm',
                             'travel_range',
                             'address',
                             'city',
                             'state',
                             'zip',
                             'gis_point']
            super(GameRequest, self).save(*args, **kwargs)
        else:
            original = GameRequest.objects.get(pk=self.pk)
            if original.request_name != self.request_name:
                update_fields.append('request_name')
            if original.system != self.system:
                update_fields.append('system')
            if original.can_dm != self.can_dm:
                update_fields.append('can_dm')
            if original.travel_range != self.travel_range:
                update_fields.append('travel_range')
            if original.address != self.address:
                update_fields.append('address')
            if original.city != self.city:
                update_fields.append('city')
            if original.state != self.state:
                update_fields.append('state')
            if original.zip != self.zip:
                update_fields.append('zip')
            if original.gis_point != self.gis_point:
                update_fields.append('gis_point')
            super(GameRequest, self).save(update_fields=update_fields, *args, **kwargs)

    def __str__(self):
        return self.request_name


# Test class for debug purposes only. Not used otherwise.
class Test(models.Model):
    Data = models.CharField(max_length=200)


# Receiver for save() on the GameRequest model.
# To avoid exceeding API rate limits or causing long page load
# times while waiting for a rate limiter to clear some data processing
# is handled as a post-save signal while the user is sent the next page.
# Does three things:
# * Check if the location coordinates need to be updated and, if so,
#   get them from the map API.
# * Check if the newly submitted request creates any valid groups
#   of players.
# * Send an email notification for any DM that has a player group
#   involving the new request.
@receiver(post_save, sender=GameRequest)
def on_save(sender, instance, created, update_fields, **kwargs):
    print("signal")
    uf = update_fields
    address_updated = False
    #Can't check for 'created' and update_fields contents in one line.
    #Throws an error on trying to iterate on None.
    #So set an address_updated flag in multiple steps.
    if created:
        address_updated = True
    if update_fields is None:
        pass
    elif 'address' in uf or 'city' in uf or 'state' in uf or 'zip' in uf:
        address_updated = True

    if address_updated:
        print(address_updated)
        if settings.USE_GEOPY_API:
            print("going to API")
            # return
            instance.gis_point = coordinates_from_api(instance.address,
                                 instance.city,
                                 instance.state,
                                 instance.zip)
            instance.save()
            return #To avoid double emails abort this post_save attempt after saving.
        elif settings.USE_FAKE_COORDINATES:
            print("fake")
            instance.gis_point = fake_coordinates()
            instance.save()
            return
        # Else leave blank coordinates intact. One of these options
        # should probably be enabled though.

    # If this person can DM call the save function for
    # every request within a 500 mile radius to update their DM list.
    # Otherwise, a DM that makes their request after a player will not appear
    # in that player's list. 500 miles because nobody will ever
    # travel that far and it cuts the volume of requests to process.
    # Since no other fields are changing this will not spawn more post_saves.
    if instance.can_dm:
        request_list = GameRequest.objects.filter(gis_point__distance_lt=(instance.gis_point, Distance(mi=500))).filter(system=instance.system)
        for r in request_list:
            r.save()

    if instance.gis_point.coords != ():
        # Find all DMs that could host this player.
        print('hosts')
        # hosts = GameRequest.objects.filter(
        #     gis_point__distance_lt=(
        #         instance.gis_point, Distance(mi=instance.travel_range))
        # ).filter(system=instance.system).filter(can_dm=True)
        for host in instance.available_dms.all():
            players = GameRequest.objects.filter(available_dms=host)
            if len(players) >= 4:
                send_email(host, players)
            #players = GameRequest.objects.filter() players with that host
            #if >= 3 players plus host send email



    # IF DM update everyone in a 500 mile radius
    # Assemble group(s)
    return 0


def send_email(dm, player_group):
    dm_email = dm.user_id.email
    subject = "Players found for " + dm.request_name + "!"
    message = "Some players are available for your game!\n"
    for players in player_group:
        message += (players.user_id.username + "     " + players.user_id.email + "\n")

    send_mail(subject,
              message,
              'notifications@gamefinder.com',
              [dm_email],
              fail_silently=True)

