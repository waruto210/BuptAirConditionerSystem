from django.urls import path, include
from .views import index, checkin, checkout

urlpatterns = [
    path('index',index),
    path('checkin', checkin),
    path('checkout', checkout),
]
