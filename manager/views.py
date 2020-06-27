'''
@Author: your name
@Date: 2020-06-01 16:17:42
@LastEditTime: 2020-06-27 15:17:18
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /django-air/manager/views.py
'''
from django.shortcuts import render
import datetime
from record_manager.RecordManager import RecordManager
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import logging
from .models import get_reports
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

logger = logging.getLogger('collect')

# Create your views here.

@csrf_exempt
def get_rpt(request):
    if request.method == 'POST':
        report_type = request.POST.get('r_type',None)
        date_from =  request.POST.get('date_from',None)
        report_list = get_reports(date_from,report_type)
        ret = {
            'code': 200,
            'msg': 'ok',
            'data': report_list
        }
        
        return JsonResponse(ret)
        


    
def index(request):
     return render(request, "manager/index.html")

