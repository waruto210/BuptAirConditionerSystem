from django.urls import path
from .views import power_off, customer, poll, get_default, power_on, change_state, pause, re_start
urlpatterns = [
    path('', customer),
    path('power_on', power_on),
    path('power_off', power_off),
    path('poll', poll),
    path('get_default', get_default),
    path('change_state', change_state),
    path('pause', pause),
    path('re_start', re_start),
]