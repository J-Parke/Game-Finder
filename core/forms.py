from django.forms import ModelForm
from .models import GameRequest


class GameRequestForm(ModelForm):
    class Meta:
        model = GameRequest
        fields = ['RequestName', 'System', 'CanDM',
                  'TravelRange', 'Address', 'City',
                  'State', 'ZIP']
        labels = {'RequestName' : 'Request name',
                  'CanDM': 'Can DM?',
                  'TravelRange': 'Travel range (miles)'
                  }
