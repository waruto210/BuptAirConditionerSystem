from django.urls import path
from .views import set_temp,checkinfo,setdefault,adm,openclose
urlpatterns = [
    path('settemp', set_temp),
    path('',adm),
    path('checkInfo',checkinfo),
    path('setdefault',setdefault),
    path('openclose',openclose)
]