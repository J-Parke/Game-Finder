from django.contrib import admin

# Register your models here.

from .models import GameRequest, Test

admin.site.register(GameRequest)
admin.site.register(Test)