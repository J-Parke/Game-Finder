from django import forms
from django.forms import ModelForm
from .models import GameRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class GameRequestForm(ModelForm):
    """
    Model form for viewing, submitting, or editing game requests.
    Hides latitude/longitude point and list of compatible DMs on the GameRequest model
    as these are not user-editable.
    """
    class Meta:
        model = GameRequest
        fields = [
            'request_name',
            'system',
            'can_dm',
            'travel_range',
            'address',
            'city',
            'state',
            'zip'
        ]
        labels = {
            'request_name': 'Request name',
            'can_dm': 'Can DM?',
            'travel_range': 'Travel range (miles)'
        }


class MyUserCreationForm(UserCreationForm):
    """
    Custom user registration form to add email address field on the signup page.
    One additional field on the form and a custom save().
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(MyUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
