from django.urls import path
from .views import set_params,checkinfo,setdefault,adm,openclose
urlpatterns = [
    path('settemp', set_params),
    path('',adm),
    path('checkInfo',checkinfo),
    path('setdefault',setdefault),
    path('openclose',openclose)
]