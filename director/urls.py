from django.urls import path, include
from .views import director, forms

urlpatterns = [
    path('', director),
    path('forms', forms)
]