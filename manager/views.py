'''
@Author: your name
@Date: 2020-06-01 16:17:42
@LastEditTime: 2020-06-01 19:16:09
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /django-air/manager/views.py
'''
from django.shortcuts import render
import datetime
from record_manager.RecordManager import RecordManager

# Create your views here.
def index(request):
    #if request.method == 'GET':
        # if 'year' and 'month' and 'day' in request.GET:
        #     y = request.GET['year']
        #     m = request.GET['month']
        #     d = request.GET['day']
        #     search_date = datetime.date(int(y), int(m), int(d))
        #     #record_list = StatisicDay.objects.filter(search_date)
        # else:
        #     print("error date!")
    
        # return render(request, 'manager/index.html',{"record_list",record_list})
    return render(request, 'manager/index.html')

