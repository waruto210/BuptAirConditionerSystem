'''
@Author: your name
@Date: 2020-06-01 16:17:42
@LastEditTime: 2020-06-26 22:15:55
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /django-air/manager/urls.py
'''
from django.urls import path, include
from .views import get_reports,index

urlpatterns = [
    path('', index),
    path('get_reports', get_reports),
]

