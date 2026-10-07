from django.contrib import admin
from .models import Account, Contribution, Event

# Register your models here.
admin.site.register(Account)
admin.site.register(Contribution)
admin.site.register(Event)
