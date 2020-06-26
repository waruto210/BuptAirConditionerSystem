from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from master.mainMachine import machine
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import logging
logger = logging.getLogger('collect')

# Create your views here.


@csrf_exempt
@login_required(login_url="/login")
def set_params(request):
    if request.method == 'POST':
        work_mode = int(request.POST.get('work_mode', None))
        sp_mpde = int(request.POST.get('sp_mode', None))
        goal_temp = int(request.POST.get('goal_temp', None))
        cold_sub = int(request.POST.get('cold_sub', None))
        cold_sup = int(request.POST.get('cold_sup', None))
        hot_sub = int(request.POST.get('hot_sub', None))
        hot_sup = int(request.POST.get('hot_sup', None))
        fee = int(request.POST.get('fee', None))
        print(type(fee))
        max_run = int(request.POST.get('max_run', None))
        machine.set_params(word_mode=work_mode, sp_mode=sp_mpde, cold_sub=cold_sub, cold_sup=cold_sup,
                           hot_sub=hot_sub, goal_temp=goal_temp,hot_sup=hot_sup, fee=fee, max_run=max_run)
        return JsonResponse({'code': '200', 'msg': 'ok'})


@csrf_exempt
@login_required(login_url="/login")
def adm(request):
    if request.method == 'GET':
        return render(request, "adm/index.html")
    if request.method == 'POST':
        opened = request.POST.getlist('opened')
        print(opened)
        if opened[0] == "on":
            machine.init_default(is_on=True)
        elif opened[0] == "off":
            machine.init_default(is_on=False)
        ion = machine.is_on()
        print(ion)
        return JsonResponse({'code': '200', 'msg': 'ok'})


@csrf_exempt
# @login_required(login_url="/login")
def checkinfo(request):
    if request.method == 'GET':
        return render(request, "adm/checkInfo.html")
    elif request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        print(room_id)
        ion = machine.is_on()
        print('the machine is' + str(ion))
        all_data = machine.check_info()
        data = machine.check_one_room(room_id=room_id)
        logger.info('data is:'+str(data))
        ret = {
            'code': 200,
            'msg': 'ok1',
            'data': data,
            'all_data': all_data
        }
        logger.info('info is: ' + str(ret))
        all_data = 0
        return JsonResponse(ret)


@csrf_exempt
@login_required(login_url="/login")
def setdefault(request):
    if request.method == 'GET':
        return render(request, "adm/setdefault.html")


@csrf_exempt
@login_required(login_url="/login")
def openclose(request):
    if request.method == 'GET':
        return render(request, "adm/openclose.html")
