from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
from core.functions import coordinates_from_api, fake_coordinates, send_email

##############
# Supported game systems for system field. This must be a fixed set of choices to
# avoid having to accommodate different abbreviations (ex: 5e vs. 5th Edition).
# If the project scales to include a non-developer admin this should
# be converted to a model so it can be managed via the admin panel.
##############
SYSTEMCHOICES = [('3.5e', 'D&D 3.5e'),
                 ('PF', 'Pathfinder'),
                 ('4e', 'D&D 4e'),
                 ('5e', 'D&D 5e'),
                 ('6e', 'D&D 6e Playtest')]


class GameRequest(models.Model):
    """
    Core game request model.
    user_id: associated User that made the request.
    request_name: display name for this request on the front end.
    system: game system the user wishes to play.
    can_dm: if the user can DM/host. For simplicity it is assumed that DMs can always host
        at their location.
    available_dms: list of potential DMs/hosts within the user's travel range. Stored in the model
        to reduce database reads when assembling a group.
    travel_range: range in miles the user is willing to travel to a game.
    address, city, state, zip: string format address submitted by user.
    gis_point: geographical coordinates of the address used in the search algorithm. Note that
        Python's Point object is (longitude, latitude) contrary to the normal map format.

    Contains a custom save() and is linked to a post_save signal for converting the address and
    finding potential game groups.
    """
    class Meta:
        unique_together = ['user', 'system']

    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
        """
        Custom save function.
        Finds all eligible DMs/hosts within the user's travel range and creates the many-to-many
        relation.
        Also sets update_fields for the post_save signal to recognize if changes to the address
        fields have been made.
        """
        update_fields = []
        # Gis_point is () if address conversion is disabled or if the API conversion fails..
        # It's fine to skip on pk = None since the address will be updated and post_save will
        # call another save() to get right back here and fill this in.
        if self.pk is not None and self.gis_point != ():
            dms = GameRequest.objects.filter(
                gis_point__distance_lt=(self.gis_point, Distance(mi=self.travel_range))).filter(
                system=self.system).filter(can_dm=True)
            for dm in dms:
                # TODO need to clear DMs that are no longer valid but set() causes errors.
                self.available_dms.add(dm)

        if self.pk is None:  # Update_fields is only valid if the database transaction is an update.
            super(GameRequest, self).save(*args, **kwargs)
        else:
            original = GameRequest.objects.get(pk=self.pk)
            for field in [
                'request_name',
                'system',
                'can_dm',
                'travel_range',
                'address',
                'city',
                'state',
                'zip',
                'gis_point'
            ]:
                if getattr(original, field) != getattr(self, field):
                    update_fields.append(field)
            super(GameRequest, self).save(update_fields=update_fields, *args, **kwargs)

    def __str__(self):
        return self.request_name


@receiver(post_save, sender=GameRequest)
def on_save(sender, instance, created, update_fields, **kwargs):
    """
    # Receiver for save() on the GameRequest model.
    To avoid causing long page load times (such as if an API rate limiter is required)
    some data processing is handled as a post-save signal while the user is sent the next page.
    Does three things:
    * Check if the location coordinates need to be updated and, if so,
        get them from the map API.
    * Check if the newly submitted request creates any valid groups
        of players.
    * Send an email notification for any DM that has a player group
        involving the new request.
    """
    address_updated = False

    # In some cases (new models or saves with no changes) update_fields will be None.
    # To avoid None errors we need to explicitly pass when update_fields is None and not
    # attempt to evaluate the if expression.

    if created:
        address_updated = True
    if update_fields is None:
        pass
    elif any([field in update_fields for field in ['address', 'city', 'state', 'zip']]):
        address_updated = True

    # Either a new model or an update to an existing address calls the address to point conversion.
    if address_updated:
        if settings.USE_GEOPY_API:
            instance.gis_point = coordinates_from_api(
                instance.address,
                instance.city,
                instance.state,
                instance.zip
            )
            instance.save()
            return  # To avoid double emails abort this post_save attempt after saving.
        # To test without calling the API use fake coordinates.
        elif settings.USE_FAKE_COORDINATES:
            instance.gis_point = fake_coordinates()
            instance.save()
            return
        # Else leave blank coordinates intact. One of these options should probably be enabled
        # though, otherwise coordinates will always be () and the search won't work.

    # If this person can DM call the save function for
    # every request within a 500 mile radius to update their DM list.
    # Otherwise, a DM that makes their request after a player will not appear
    # in that player's list. 500 miles because nobody will ever
    # travel that far and it cuts the volume of requests to process.
    # Since no other fields are changing this will not spawn more post_saves.
    if instance.can_dm:
        request_list = GameRequest.objects.filter(
            gis_point__distance_lt=(instance.gis_point, Distance(mi=500)),
            system=instance.system
        )
        for r in request_list:
            # TODO potential scaling issue, can this be done with fewer database transactions?
            r.save()

    if instance.gis_point.coords != ():
        # Find all DMs that could host this player.
        for host in instance.available_dms.all():
            # Find all players that list this DM as a possible host.
            players = GameRequest.objects.filter(available_dms=host)
            if len(players) >= 4:  # DM and 3+ players is a typical game group.
                send_email(host, players)
