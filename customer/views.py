from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Customer
from datetime import datetime
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.

def customer(request):
    if request.method == 'GET':
        return render(request, "customer/control.html")


def push(msg):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'push',
        {
            'type': 'push.song',
            'msg': msg
        }
    )

def get_time(request):
    if request.method == 'GET':
        stamp = datetime.now()
        ret = {'time': str(stamp)}
        push('another get_time')
        return JsonResponse(ret)
