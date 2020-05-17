from django.urls import path
from .views import customer, get_time, power, poll
urlpatterns = [
    path('', customer),
    path('get_time', get_time),
    path('power', power),
    path('poll', poll),
]