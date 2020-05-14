from django.urls import path
from .views import set_temp
urlpatterns = [
    path('settemp', set_temp),
]