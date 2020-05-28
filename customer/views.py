from operator import attrgetter
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Customer, State, Ticket, StatisicDay, create_new_ticket, get_current_ticket
import time
from django.views.decorators.csrf import csrf_exempt
import math
from master.mainMachine import machine, cal_service_cost_temp, cal_wait_temp, cal_pause_temp, change_temp_rate
import datetime
import logging
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
        print('ret is: ', ret)
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
        curr_temp = int(request.POST.get('curr_temp', None))
        sp_mode = int(request.POST.get('sp_mode', None))
        work_mode = int(request.POST.get('work_mode', None))
        # 确认是否登记入住了
        # try:
        #     Customer.objects.get(RoomId=room_id)
        # except Exception:
        #     print("here")
        #     ret['code'] = 1001
        #     ret['msg'] = "当前房间未登记入住"
        #     return JsonResponse(ret)
        state, _ = State.objects.get_or_create(room_id=room_id)
        state.goal_temp = goal_temp
        state.curr_temp = curr_temp
        state.sp_mode = sp_mode
        state.work_mode = work_mode
        state.is_on = True
        state.is_work = False
        state.save()

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

        # 确认是否登记入住了
        # try:
        #     Customer.objects.get(RoomId=room_id)
        # except Exception:
        #     print("here")
        #     ret['code'] = 1001
        #     ret['msg'] = "当前房间未登记入住"
        #     return JsonResponse(ret)
        state = State.objects.get(room_id=room_id)
        state.is_on = False
        state.is_work = False
        state.save()
        ticket = get_current_ticket(room_id, phone_num)
        ticket.end_time = datetime.datetime.now()
        ticket.save()
        # 删除调度队列中的slave对象
        machine.lock.acquire()
        try:
            machine.delete_if_exists(room_id)
            machine.wait_to_service()
        finally:
            machine.lock.release()
        ret['data'] = data
        return JsonResponse(ret)


@csrf_exempt
def change_state(request):
    if request.method == 'POST':
        ins = request.POST.get('ins', None)
        room_id = request.POST.get('room_id', None)
        phone_num = request.POST.get('phone_num', None)
        goal_temp = float(request.POST.get('goal_temp', None))
        work_mode = int(request.POST.get('work_mode', None))
        if ins == 'change_sp':
            pre_sp = int(request.POST.get('pre_sp', None))
            sp_mode = int(request.POST.get('sp_mode', None))
            logger.info("room_id: " + str(room_id) + " 更改风速为: " + str(sp_mode))
            # 开机后的立即请求,新建ticket
            if pre_sp == -1:
                ticket = create_new_ticket(room_id, phone_num, sp_mode)
            else:
                # 否则取当前ticket的单子
                ticket = get_current_ticket(room_id, phone_num)
                if ticket.schedule_count == 0:
                    # 如果上次请求未被调度，则作为新的ticket
                    ticket.start_time = datetime.datetime.now()
                    ticket.sp_mode = sp_mode
                else:
                    # 保存上次ticket，新建ticket
                    ticket.end_time = datetime.datetime.now()
                    ticket.save()
                    ticket = create_new_ticket(room_id, phone_num, sp_mode)
            ticket.save()
            # 处理新请求
            machine.lock.acquire()
            try:
                # 删掉旧请求，调度等待队列
                machine.delete_if_exists(room_id)
                machine.wait_to_service()
                # 加入新请求
                machine.new_request(room_id=room_id, phone_num=phone_num, req_time=int(time.time()), sp_mode=sp_mode)
            finally:
                machine.lock.release()
        elif ins == 'change_goal':
            logger.info("room_id: " + str(room_id) + " 更改目标温度为: " + str(goal_temp))
            state = State.objects.get(room_id=room_id)
            state.goal_temp = goal_temp
            state.save()
        elif ins == 'change_mode':
            logger.info("room_id: " + str(room_id) + " 更改温控模式为: " + str(work_mode))
            state = State.objects.get(room_id=room_id)
            state.work_mode = work_mode
            state.save()
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
            cal_pause_temp(room_id, phone_num)

        state = State.objects.get(room_id=room_id)
        curr_temp = state.curr_temp
        total_cost = state.total_cost
        is_work = state.is_work
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
        machine.lock.acquire()
        logger.info('room_id: ' + str(room_id) + " 达到目标温度")
        try:
            # 将当前房间加入停止队列
            machine.move_to_pause(room_id)
            # 选择一个等待状态的放假加入服务队列
            machine.wait_to_service()
        finally:
            machine.lock.release()
        return JsonResponse({'code': 200, 'msg': 'ok'})


@csrf_exempt
def re_start(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        phone_num = request.POST.get('phone_num', None)
        logger.info('room_id:' + str(room_id) + " 温差达到1度")
        machine.lock.acquire()
        try:
            s = machine.delete_pause(room_id)
            machine.new_request(room_id=s.room_id, phone_num=phone_num, req_time=int(time.time()), sp_mode=s.sp_mode)
        finally:
            machine.lock.release()
        state = State.objects.get(room_id=room_id)
        is_work = state.is_work
        return JsonResponse({'code': 200, 'msg': 'ok', 'is_work': is_work})


def customer(request):
    if request.method == 'GET':
        if machine.is_on():
            return render(request, "customer/index_copy.html")
        else:
            return HttpResponse("中央空调未开机")

