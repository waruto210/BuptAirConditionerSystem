from django.db import models
from customer.models import StatisicDay,Record,Ticket
from datetime import datetime,timedelta,date
import logging
from django.core import serializers
from collections import defaultdict
logger = logging.getLogger('collect')

# Create your models here.

def add_reports(rooms_info,report_type,date_to,date_from):
    for room in rooms_info:
        room_id = room
        report_type = rooms_info[room]['report_type']
        date = rooms_info[room]['date']
        oc_count = rooms_info[room]['oc_count']
        logger.info("oc_count: " +str(oc_count))
        common_temp = max(rooms_info[room]['temp_dict'],key=rooms_info[room]['temp_dict'].get)
        choice = max(rooms_info[room]['sp_dict'],key=rooms_info[room]['sp_dict'].get)
        achieve_count = rooms_info[room]['achieve_count']
        ticket_count = rooms_info[room]['ticket_count']
        total_cost = rooms_info[room]['total_cost']
        schedule_count = rooms_info[room]['schedule_count']
        r = StatisicDay.objects.create(room_id=room_id, report_type=report_type,schedule_count=schedule_count,
                date=date, oc_count=oc_count,common_temp=common_temp, common_spd=choice,
                achieve_count=achieve_count,ticket_count=ticket_count, total_cost= total_cost)
    rooms = list(StatisicDay.objects.filter(date=date_from,report_type=report_type))
    if datetime.now().__lt__(date_to):   
        StatisicDay.objects.filter(date=date_from,report_type=report_type).delete()
        r.save()
    rooms = list(StatisicDay.objects.filter(date=date_from,report_type=report_type))
    return rooms



def add_day_report(date,report_type):

    if report_type == 'd':
        date_from,date_to = date,date + timedelta(days=1)
    elif report_type == 'w':
        date_from,date_to = date,date + timedelta(days=8)
    elif report_type == 'm':
        date_from,date_to = date,date + timedelta(days=31)
    elif report_type == 'y':
        date_from,date_to = date,date + timedelta(days=366)
    logger.info("date_from: " +str(date_from))
    logger.info("date_to: " +str(date_to))

    r1 = list(Record.objects.filter(at_time__range=(date_from,date_to)))
    room_list = []
    rooms_info = {}
    for i in r1:
        if i.room_id not in room_list:
            room_list.append(i.room_id)
    rooms = list(StatisicDay.objects.filter(date=date_from,report_type=report_type))
    if rooms == [] or datetime.now().__lt__(date_to):
        for room in room_list:
            r_info = {'report_type':report_type,'date':date_from,'oc_count':0,'temp_dict':defaultdict(int),'sp_dict':defaultdict(int),
                        'achieve_count':0,'ticket_count':0,'total_cost':0,'schedule_count':0}
            r3 = list(Record.objects.filter(room_id=room,at_time__range=(date_from,date_to)))
            r4 = list(Ticket.objects.filter(room_id=room,start_time__range=(date_from,date_to)))
            for i in r3:
                if i.record_type == 'power_on':
                    r_info['oc_count'] += 1  #开关机次数
                if i.record_type == 'goal_temp':
                    if i.duration:
                        r_info['temp_dict'][i.goal_temp] += i.duration #常用目标温度
                        r_info['achieve_count'] += 1 #达到目标温度次数
            for i in r4:
                r_info['sp_dict'][i.sp_mode] += i.duration #常用风速
                r_info['ticket_count'] += 1 #详单记录数
                r_info['total_cost'] += i.cost # 总费用
                r_info['schedule_count'] += i.schedule_count #成功调度次数
            rooms_info[room] = r_info
    rooms = add_reports(rooms_info,report_type,date_to,date_from)
    return rooms

# 查询不同类型的报表
def get_reports(date_from,report_type):
    dfrom = date_from.split('/')
    date_from = datetime(int(dfrom[2]),int(dfrom[0]),int(dfrom[1]))
    res = add_day_report(date_from,report_type)
    return serializers.serialize("json", res)



