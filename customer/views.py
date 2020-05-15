from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Customer, State
from datetime import datetime
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from master.main_machine import machine
from django.views.decorators.csrf import csrf_exempt
import math
# Create your views here.

@csrf_exempt
def poweron(request):
    ret = {
        'code': 200,
        'msg': 'ok',
    }
    data = {}
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        ins = request.POST.get('ins', None)
        goal_temp = float(request.POST.get('goal_temp', None))
        curr_temp = float(request.POST.get('curr_temp', None))
        sp_mode = request.POST.get('sp_mode', None)
        work_mode = request.POST.get('work_mode', None)
        total_cost = request.POST.get('total_cost', None)
        
        state, flag = State.objects.get_or_create(room_id=room_id)

        state.goal_temp = goal_temp
        state.curr_temp = curr_temp
        state.sp_mode = sp_mode
        state.work_mode = work_mode
        state.total_cost = total_cost
        state.save()
        if math.isclose(curr_temp, goal_temp):
            data['is_work'] = False
        else:
            data['is_work'] = True
        ret['data'] = data
        return JsonResponse(ret)
        
@csrf_exempt
def poll(request):
    ret = {
        'code': 200,
        'msg': 'ok',
    }
    data = {}
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        ins = request.POST.get('ins', None)
        goal_temp = float(request.POST.get('goal_temp', None))
        curr_temp = float(request.POST.get('curr_temp', None))
        sp_mode = request.POST.get('sp_mode', None)
        work_mode = request.POST.get('work_mode', None)
        total_cost = request.POST.get('total_cost', None)
        
        state = State.objects.get(room_id=room_id)

        state.goal_temp = goal_temp
        state.curr_temp = curr_temp
        state.sp_mode = sp_mode
        state.work_mode = work_mode
        state.total_cost = total_cost
        state.save()
       
        if math.isclose(curr_temp, goal_temp):
            data['is_work'] = False
        else:
            data['is_work'] = True
        ret['data'] = data
        return JsonResponse(ret)


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
