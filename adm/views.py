from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from master.main_machine import machine
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def set_temp(request):
    if request.method == 'POST':
        goal_temp = request.POST.get('goal_temp', None)
        env_temp = request.POST.get('env_temp', None)
        if goal_temp != None and env_temp != None:
            machine.set_temp(goal_temp, env_temp)
            return JsonResponse({'result': 'ok', 'msg': 'ok'})
        else:
            return JsonResponse({'result': 'err', 'msg': 'para erros'})