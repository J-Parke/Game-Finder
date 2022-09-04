from django.shortcuts import render
# from django.contrib.auth import user
from django.http import HttpResponse, HttpResponseRedirect
from .models import GameRequest
from .forms import GameRequestForm
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point, GEOSGeometry

# Create your views here.


def index(request):
    if request.user.is_authenticated:
        GameRequestList = GameRequest.objects.filter(UserID=request.user)[:100]
        context = {'GameRequestList': GameRequestList}
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html')
    return HttpResponse("Arrived at broken index page.")


def details(request, GameRequestID=0):
    if GameRequestID:
        GameRequestInstance = get_object_or_404(GameRequest, pk=GameRequestID)
        form = GameRequestForm(instance=GameRequestInstance)
        if True: #form.is_valid():
            context = {'form': form, 'RequestID': GameRequestID}
            return render(request, 'details.html', context)
    else:
        form = GameRequestForm()
        context = {'form': form, 'RequestID': 0}
        return render(request, 'details.html', context)
    return HttpResponse("Arrived at broken detail page.")


def submit(request, GameRequestID=0):
    if request.method == 'POST':
        if GameRequestID:
            old = get_object_or_404(GameRequest, pk=GameRequestID)
            f = GameRequestForm(request.POST, instance=old)
            f.TravelRange = 999
            f.save()
            return HttpResponse("Please don't break my system 1.")
        else:
            f = GameRequestForm(request.POST)
            #f.GISPoint = GEOSGeometry('POINT(%s %s), 4236' % (0,0))
            pnt = Point(0,0)
            f.instance.GISPoint = pnt
            f.save()
            return HttpResponse("Please don't break my system 2.")
    else:
        return HttpResponse("Please don't break my system 3.")


def hello(request):
    return HttpResponse("Hello world!")
