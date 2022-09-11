from django.shortcuts import render
# from django.contrib.auth import user
from django.http import HttpResponse, HttpResponseRedirect
from .models import GameRequest
from .forms import GameRequestForm
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.gis.geos import Point, GEOSGeometry


# Create your views here.

# Index page.
# Provides a list of a user's active game requests (if logged in) or
# redirects to the login page (if not).
def index(request):
    if request.user.is_authenticated:
        GameRequestList = GameRequest.objects.filter(user_id=request.user)[:100]
        context = {'GameRequestList': GameRequestList}
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html')
    return HttpResponse("Arrived at broken index page.")

# Individual request details page.
# Optional argument: database ID for an existing game request.
# If one is provided the page is populated with the current
# information and the user can edit or delete the request.
# Otherwise a blank form is provided.
def details(request, GameRequestID=0):
    if GameRequestID:
        GameRequestInstance = get_object_or_404(GameRequest, pk=GameRequestID)
        form = GameRequestForm(instance=GameRequestInstance)
       # if form.is_valid(): should be validated but this breaks even when it looks fine?
        context = {'form': form, 'RequestID': GameRequestID}
        return render(request, 'details.html', context)
    else:
        # Need to get rid of the delete button on a blank form.
        form = GameRequestForm()
        context = {'form': form, 'RequestID': 0}
        return render(request, 'details.html', context)
    return HttpResponse("Arrived at broken detail page.")


def submit(request, GameRequestID=0):
    if request.method == 'POST':
        if GameRequestID:
            old = get_object_or_404(GameRequest, pk=GameRequestID)
            f = GameRequestForm(request.POST, instance=old)
            f.save()
            return HttpResponseRedirect(reverse('core:index'), request)
        else:
            f = GameRequestForm(request.POST)
            f.instance.user_id = request.user
            f.save()
            return HttpResponseRedirect(reverse('core:index'), request)
    else:
        return HttpResponse("Please don't break my system.")


def delete(request, GameRequestID=None):
    #return HttpResponse(GameRequestID)
    r = get_object_or_404(GameRequest, pk=GameRequestID)
    r.delete()
    return HttpResponseRedirect(reverse('core:index'), request)


def hello(request):
    return HttpResponse("Hello world!")


def fake_coordinates():
    # 935 East 8th St. +/- a mile or three.
    location = Point(48.10649195214683, -123.42273912049563)
    x_shift = random.uniform(-0.02, 0.02)
    y_shift = random.uniform(-0.02, 0.02)
    location.x += x_shift
    location.y += y_shift
    return location
