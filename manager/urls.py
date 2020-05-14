from django.urls import path, include
from .views import add, checkout

urlpatterns = [
    path('add', add),
    path('checkout', checkout),
]
