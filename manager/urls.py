from django.urls import path, include
from .views import index, login_manager, logout_manager, add, checkout

urlpatterns = [
    path('', index),
    path('login', login_manager),
    path('logout', logout_manager),
    path('add', add),
    path('checkout', checkout),
]
