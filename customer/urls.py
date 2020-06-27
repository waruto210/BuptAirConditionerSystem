from django.urls import path
from .views import power_off, customer, poll, get_default, power_on, change_fan_speed, \
    change_goal_temp, change_work_mode, pause, re_start, off_rate, verify

urlpatterns = [
    path('', customer),
    path('power_on', power_on),
    path('power_off', power_off),
    path('poll', poll),
    path('get_default', get_default),
    path('change_fan_speed', change_fan_speed),
    path('change_goal_temp', change_goal_temp),
    path('change_work_mode', change_work_mode),
    path('pause', pause),
    path('re_start', re_start),
    path('off_rate', off_rate),
    path('verify', verify),
]
