from django.urls import path, include
from .views import index, add, checkout

urlpatterns = [
    path('index',index),
    path('add', add),
    path('checkout', checkout),
]
