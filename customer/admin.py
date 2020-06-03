from django.contrib import admin
from .models import Customer, State, Ticket
# Register your models here.
admin.site.register(Customer)
admin.site.register(State)
admin.site.register(Ticket)