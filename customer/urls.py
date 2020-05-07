from django.urls import path
from .views import customer, get_time
urlpatterns = [
    path('', customer),
    path('get_time', get_time)
]
