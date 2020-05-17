from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Customer, State
from datetime import datetime
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
import math
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from master.main_machine import machine

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')


@register_job(scheduler, 'interval', id='scheduler', seconds=25)
def bg_job():
    machine.lock.acquire()
    try:
        l = len(machine.wait_queue)
        if l > machine.max_run and \
                machine.wait_queue[machine.max_run - 1].is_pause == 0 and \
                machine.wait_queue[machine.max_run].is_pause == 0 and \
                machine.wait_queue[machine.max_run - 1].sp_mode == machine.wait_queue[machine.max_run].sp_mode:
            machine.wait_queue[machine.max_run - 1].req_time = int(time.time())
    finally:
        machine.lock.release()


register_events(scheduler)
scheduler.start()



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
            is_pause = 1
        else:
            is_pause = 0
        machine.lock.acquire()
        data['is_work'] = False
        try:
            machine.add_slave(room_id=room_id, req_time=int(time.time()),
                              sp_mode=int(sp_mode), is_pause=is_pause)
            machine.schedule()
            data['is_work'] = machine.get_is_work(room_id=room_id)
        finally:
            machine.lock.release()
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
        sp_mode = int(request.POST.get('sp_mode', None))
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
            is_pause = 1
        else:
            is_pause = 0
        data['is_work'] = True
        if is_pause == 0:
            machine.lock.acquire()
            try:
                pre_is_pause = machine.get_is_pause(room_id)
                # 如果之前是达到目标温度，暂停送风
                if pre_is_pause == 1:
                    # 差距达到1度
                    if math.fabs(curr_temp - goal_temp) >= 1:
                        # 继续申请送风
                        is_pause = 0
                        machine.set_pause(room_id, is_pause)
                if ins == "change_sp":
                    machine.change_sp(room_id, sp_mode)
                machine.schedule()
                data['is_work'] = machine.get_is_work(room_id)
            finally:
                machine.lock.release()
        else:
            machine.lock.acquire()
            try:
                machine.set_pause(room_id, is_pause)
                if ins == "change_sp":
                    machine.change_sp(room_id, sp_mode)
                machine.schedule()
                data['is_work'] = machine.get_is_work(room_id)
            finally:
                machine.lock.release()

        ret['data'] = data
        return JsonResponse(ret)


def customer(request):
    if request.method == 'GET':
        env_temp = machine.get_temp()
        if env_temp is not None:
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
