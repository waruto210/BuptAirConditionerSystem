from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from master.mainMachine import machine
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def set_params(request):
    if request.method == 'POST':
        work_mode = request.POST.get('work_mode', None)
        env_temp = request.POST.get('env_temp', None)
        cold_sub = request.POST.get('cold_sub', None)
        cold_sup = request.POST.get('cold_sup', None)
        hot_sub = request.POST.get('hot_sub', None)
        hot_sup = request.POST.get('hot_sup', None)
        fee = request.POST.get('fee', None)
        max_run = request.POST.get('max_run', None)

        machine.set_params(word_mode=work_mode, env_temp=env_temp, cold_sub=cold_sub, cold_sup=cold_sup,
                           hot_sub=hot_sub, hot_sup=hot_sup, fee=fee, max_run=max_run)
        return JsonResponse({'code': '200', 'msg': 'ok'})

@csrf_exempt
def adm(request):
    if request.method == 'GET':
        print('get!')
        return render(request, "adm/index.html")
    if request.method == 'POST':
        opened = request.POST.getlist('opened')
        print(opened)
        return 'success'

def checkinfo(request):
    if request.method == 'GET':
        return render(request, "adm/checkInfo.html")


def setdefault(request):
    if request.method == 'GET':
        return render(request, "adm/setdefault.html")


def openclose(request):
    if request.method == 'GET':
        return render(request, "adm/openclose.html")
