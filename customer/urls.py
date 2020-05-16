from django.urls import path
from .views import customer, get_time, poweron, poll
urlpatterns = [
    path('', customer),
    path('get_time', get_time),
    path('poweron', poweron),
    path('poll', poll),
]