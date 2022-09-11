from django.contrib.gis.geos import Point
from functools import lru_cache
from geopy.geocoders import Nominatim
from django.core.mail import send_mail
import random


# Get latitude/longitude coordinates for an address (for distance search).
# Uses geopy library: https://geopy.readthedocs.io/en/stable/
# Currently uses the Nominatim API. This is a free service with
# significant rate limitations. Making GameFinder a real product
# will require replacing Nominatim with a paid service that can
# accommodate sufficient requests per minute.
@lru_cache(maxsize=512)
def coordinates_from_api(street, city, state, zip_code):
    print("api1")
    geolocator = Nominatim(user_agent="GameFinder")
    print("api2")
    address_string = street + ' ' + city + ' ' + state + ' ' + zip_code
    print("api3")
    location = geolocator.geocode(address_string)
    print("api4")
    return Point(location.longitude, location.latitude)


# Creates fake coordinates for testing purposes to avoid exceeding
# rate limits on the (free but limited) map API.
# Starting point is in Port Angeles, WA. A small random shift
# is applied to both latitude and longitude and the result is returned
# as a Point object to be saved in the GameRequest.
def fake_coordinates():
    # 935 East 8th St. +/- a mile or three.
    location = Point(-123.42273912049563, 48.10649195214683)
    lat_shift = random.uniform(-0.02, 0.02)
    lon_shift = random.uniform(-0.02, 0.02)
    location.y += lat_shift
    location.x += lon_shift
    return location


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
