from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Customer
from datetime import datetime
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from master.main_machine import machine
# Create your views here.

def customer(request):
    if request.method == 'GET':
        env_temp = machine.get_temp()
        if env_temp != None:
            return render(request, "customer/control.html", {'env_temp': env_temp})
        else:
            return HttpResponse("中央空调未开机")


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
