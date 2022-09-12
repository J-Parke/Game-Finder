from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import GameRequest
from .forms import GameRequestForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def index(request):
    """
    Index page.
    Provides a list of a user's active game requests (if logged in) or
    a link to the login page (if not).
    """
    if request.user.is_authenticated:
        GameRequestList = GameRequest.objects.filter(user_id=request.user)[:100]
        context = {'GameRequestList': GameRequestList}
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html')


@login_required
def details(request, GameRequestID=0):
    """
    Individual request details page.
    Optional argument: database ID for an existing game request.
    If one is provided the page is populated with the current
    information and the user can edit or delete the request.
    Otherwise a blank form is provided.
    """
    if GameRequestID:
        GameRequestInstance = get_object_or_404(GameRequest, pk=GameRequestID, user_id=request.user)
        form = GameRequestForm(instance=GameRequestInstance)
        # TODO if form.is_valid(): should be validated but this breaks even when it looks fine?
        context = {'form': form, 'RequestID': GameRequestID}
        return render(request, 'details.html', context)
    else:
        # TODO Need to get rid of the delete button on a blank form.
        form = GameRequestForm()
        context = {'form': form, 'RequestID': 0}
        return render(request, 'details.html', context)


@require_POST
@login_required
def submit(request, GameRequestID=0):
    """
    Submit target for the game request form.
    If ID is 0 the form is from the "new request" link and goes into the database as a new object.
    If the form is sent with a non-zero ID by the request's owner it updates the existing request.
    Note that this model has an overwritten save() and extensive post_save processing.
    """
    if GameRequestID:
        old = get_object_or_404(GameRequest, pk=GameRequestID, user_id=request.user)
        f = GameRequestForm(request.POST, instance=old)
        f.save()
        return HttpResponseRedirect(reverse('core:index'), request)
    else:
        f = GameRequestForm(request.POST)
        f.instance.user_id = request.user
        f.save()
        return HttpResponseRedirect(reverse('core:index'), request)


@login_required
def delete(request, GameRequestID=None):
    """
    Delete target for the game request form.
    """
    r = get_object_or_404(GameRequest, pk=GameRequestID, user_id=request.user)
    r.delete()
    return HttpResponseRedirect(reverse('core:index'), request)
