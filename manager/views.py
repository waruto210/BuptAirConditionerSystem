'''
@Author: your name
@Date: 2020-06-01 16:17:42
@LastEditTime: 2020-06-26 22:17:37
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /django-air/manager/views.py
'''
from django.shortcuts import render
import datetime
from record_manager.RecordManager import RecordManager
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url="/login")
def get_reports(request):
    if request.method == 'GET':
        report_type = request.GET('reporttype')
        date_from =  request.GET('date_from')
        date_to =  request.GET('date_to')
        report_list = get_reports(report_type,date_from,date_to)
        paginator = Paginator(report_list, 10, 1)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
        return render(request, 'manager/index.html', {"report_list": report_list})

def index(request):
     return render(request, "manager/index.html")
