from django.db import models
from customer.models import StatisicDay,Record

# Create your models here.



def add_report(rooms_info):
    for room in rooms_info:
        room_id = room
        report_type = rooms_info[room]['report_type']
        date = rooms_info[room]['date']
        oc_count = rooms_info[room]['oc_count']
        common_temp = max(rooms_info[room]['temp_dict'],key=rooms_info[room]['temp_dict'].get)
        choice = max(rooms_info[room]['sp_dict'],key=rooms_info[room]['sp_dict'].get)
        achieve_count = rooms_info[room]['achieve_count']
        ticket_count = rooms_info[room]['ticket_count']
        total_cost = rooms_info[room]['total_cost']
        schedule_count = rooms_info[room]['schedule_count']
        r = StatisicDay.objects.create(room_id=room_id, report_type=report_type,schedule_count=schedule_count,
                date=date, oc_count=oc_count,common_temp=common_temp,choice=choice,
                achieve_count=achieve_count,ticket_count=ticket_count, total_cost= total_cost)
        r.save()
    return r

def add_day_report(date):
    r1 = list(Record.objects.filter(date__day=date))
    room_list = []
    rooms_info = []
    for i in r1:
        if i.room_id not in room_list:
            add_report(i.room_id,date)
    for room in room_list:
        r_info = {'report_type':'d','date':date,'oc_count':0,'temp_dict':{},'sp_dict':{},
                    'achieve_count':0,'ticket_count':0,'total_cost':0,'schedule_count':0}
        r3 = list(Record.objects.filter(room=room,date__day=date))
        r4 = list(Ticket.objects.filter(room=room,start_time__day=date))
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
    add_reports(room_list,rooms_info)
    return rooms_info

# 查询不同类型的报表
def get_reports(date_from,date_to,report_type):
    if report_type == 'd':
        res = StatisicDay.objects.filter(date__day=date_from)
        if res ==[]:
            res = add_day_report(date_from)
        return res
    elif report_type == 'w':
        # for i in range((date_to - date_from).days + 1):
        #     day = date_from + datetime.timedelta(days=i)
        #     res = StatisicDay.objects.filter(date__gt=date_from,date__lt=date)) 
        #     if res == []:
        pass
    elif report_type == 'm':
        pass
    elif report_type == 'y':
        pass




