from operator import attrgetter
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Customer, State, init_state
from django.views.decorators.csrf import csrf_exempt
import math
from master.mainMachine import machine, cal_service_cost_temp, cal_wait_temp, cal_pause_temp, change_temp_rate
import datetime
import logging
from record_manager.RecordManager import RecordManager

logger = logging.getLogger('collect')


@csrf_exempt
def get_default(request):
    if request.method == 'GET':
        ret = {
            'code': 200,
            'msg': 'ok',
        }
        data = {}

        params = list(machine.get_params())
        print('param is: ', params)
        data['work_mode'] = params[0]
        data['sp_mode'] = params[1]
        data['cold_sub'] = params[2]
        data['cold_sup'] = params[3]
        data['hot_sub'] = params[4]
        data['hot_sup'] = params[5]
        data['env_temp'] = params[6]

        ret['data'] = data
        logger.info('default params is: ' + str(ret))
        return JsonResponse(ret)


@csrf_exempt
def power_on(request):
    if request.method == 'POST':
        ret = {
            'code': 200,
            'msg': 'ok'
        }
        data = {}
        room_id = request.POST.get('room_id', None)
        phone_num = request.POST.get('phone_num', None)
        goal_temp = int(request.POST.get('goal_temp', None))
        sp_mode = int(request.POST.get('sp_mode', None))
        work_mode = int(request.POST.get('work_mode', None))
        # 确认是否登记入住了
        try:
            Customer.objects.get(RoomId=room_id, PhoneNum=phone_num)                
        except Exception:
            logger.info('Can\'t find customer')
            ret['code'] = 1001
            ret['msg'] = "当前房间及对应手机号未在前台登记，是否输入错误？"
            return JsonResponse(ret)

        logger.info("room_id: " + room_id + "开机")
        RecordManager.add_power_on_record(room_id)
        # 新建ticket和record
        RecordManager.add_goal_temp_record(room_id, goal_temp)
        RecordManager.add_ticket(room_id, phone_num, sp_mode)
        data['is_work'] = machine.one_room_power_on(room_id=room_id, phone_num=phone_num, goal_temp=goal_temp, sp_mode=sp_mode, work_mode=work_mode)

        ret['data'] = data
        return JsonResponse(ret)


@csrf_exempt
def power_off(request):
    if request.method == 'POST':
        ret = {
            'code': 200,
            'msg': 'ok'
        }
        data = {}
        room_id = request.POST.get('room_id', None)
        phone_num = request.POST.get('phone_num', None)

        RecordManager.add_power_off_record(room_id)

        RecordManager.finish_goal_temp_record(room_id)

        RecordManager.finish_ticket(room_id, phone_num)
        # 删除调度队列中的slave对象
        logger.info("room_id: " + room_id + "关机")
        machine.one_room_power_off(room_id)
        ret['data'] = data
        return JsonResponse(ret)


@csrf_exempt
def change_fan_speed(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        phone_num = request.POST.get('phone_num', None)
        sp_mode = int(request.POST.get('sp_mode', None))
        logger.info("room_id: " + str(room_id) + " 更改风速为: " + str(sp_mode))
        RecordManager.finish_ticket(room_id, phone_num)
        RecordManager.add_ticket(room_id, phone_num, sp_mode)

        # 处理新请求
        machine.change_fan_speed(room_id=room_id, phone_num=phone_num, sp_mode=sp_mode)

        ret = {
            'code': 200,
            'msg': 'ok',
            'data': {},
        }
        return JsonResponse(ret)

@csrf_exempt
def change_goal_temp(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        goal_temp = int(request.POST.get('goal_temp', None))

        RecordManager.finish_goal_temp_record(room_id)
        RecordManager.add_goal_temp_record(room_id, goal_temp)
        logger.info("room_id: " + str(room_id) + " 更改目标温度为: " + str(goal_temp))
        machine.change_goal_temp(room_id=room_id, goal_temp=goal_temp)
        ret = {
            'code': 200,
            'msg': 'ok',
            'data': {},
        }
        return JsonResponse(ret)

@csrf_exempt
def change_work_mode(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        work_mode = int(request.POST.get('work_mode', None))
        RecordManager.add_work_mode_record(room_id)
        logger.info("room_id: " + str(room_id) + " 更改温控模式为: " + str(work_mode))
        machine.change_work_mode(room_id=room_id, work_mode=work_mode)
        ret = {
            'code': 200,
            'msg': 'ok',
            'data': {},
        }
        return JsonResponse(ret)

@csrf_exempt
def poll(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        phone_num = request.POST.get('phone_num', None)
        pos = machine.get_queue_pos(room_id)
        if pos == 'service':
            cal_service_cost_temp(room_id, phone_num)
        elif pos == 'wait':
            cal_wait_temp(room_id)
        else:
            cal_pause_temp(room_id)

        curr_temp, total_cost, is_work = machine.get_one_room_state(room_id)
        ret = {
            'code': 200,
            'msg': 'ok',
            'data': {
                'is_work': is_work,
                'curr_temp': curr_temp,
                'total_cost': total_cost,
            }
        }
        return JsonResponse(ret)


@csrf_exempt
def pause(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        phone_num = request.POST.get('phone_num', None)
        logger.info('room_id: ' + str(room_id) + " 达到目标温度")
        RecordManager.add_reach_goal_record(room_id)

        machine.one_room_pause(room_id)
        return JsonResponse({'code': 200, 'msg': 'ok'})


@csrf_exempt
def re_start(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        phone_num = request.POST.get('phone_num', None)
        logger.info('room_id:' + str(room_id) + " 温差达到1度")

        is_work = machine.one_room_restart(room_id, phone_num)
        return JsonResponse({'code': 200, 'msg': 'ok', 'is_work': is_work})


def customer(request):
    if request.method == 'GET':
        if machine.is_on():
            return render(request, "customer/index_copy.html")
        else:
            return HttpResponse("中央空调未开机")
