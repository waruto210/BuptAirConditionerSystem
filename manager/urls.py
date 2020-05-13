from django.urls import path, include
from .views import logout_manager, add, checkout

urlpatterns = [
    path('logout', logout_manager),
    path('add', add),
    path('checkout', checkout),
]
