from django.urls import path
from django.contrib import admin

from . import views

app_name = 'core'

urlpatterns = [
    # Home page with index of user's game requests.
    path('', views.index, name='index'),
    # View details of a single event and modify/delete.
    path('details/<int:GameRequestID>/', views.details, name='details'),
    path('details/', views.details, name='new request'),
    # Form submission target.
    path('submit/<int:GameRequestID>', views.submit, name='submit'),
    # Delete the request a form is attached to.
    path('delete/<int:GameRequestID>', views.delete, name='delete'),
    # Server debug only.
    path('hello/', views.hello, name='hello')
]
