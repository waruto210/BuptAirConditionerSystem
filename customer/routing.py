from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    re_path('^ws/tuisong/$', consumers.Tuisong),
]