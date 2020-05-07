from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Customer
from datetime import datetime
import time
# Create your views here.

def customer(request):
    if request.method == 'GET':
        return render(request, "customer/control.html")


def get_time(request):
    if request.method == 'GET':
        stamp = datetime.now()
        ret = {'time': str(stamp)}
        return JsonResponse(ret)