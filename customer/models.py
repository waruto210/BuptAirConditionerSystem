from django.db import models
import datetime

# Create your models here.
class Customer(models.Model):
    Name = models.CharField(max_length=50)
    RoomId = models.CharField(max_length=20)

    def __str__(self):
        return "房间号: " + self.RoomId + "   " + self.Name


class State(models.Model):
    room_id = models.CharField(max_length=20, primary_key=True)
    # RoomId = models.ForeignKey('Customer',on_delete=models.CASCADE)
    is_on = models.BooleanField(default=False)
    is_work = models.BooleanField(default=False)
    choice1 = (
        (1, 'hot'),
        (0, 'cold'),
    )
    work_mode = models.IntegerField(choices=choice1, null=True)
    choice2 = (
        (0, 'low'),
        (1, 'middle'),
        (2, 'high'),
    )
    sp_mode = models.IntegerField(choices=choice2, null=True)
    goal_temp = models.IntegerField(null=True)
    curr_temp = models.FloatField(null=True)
    total_cost = models.FloatField(default=0)


class Ticket(models.Model):
    room_id = models.CharField(max_length=20)
    phone_num = models.CharField(max_length=20)
    ticket_id = models.IntegerField(default=0)

    # 开机 换风速
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    # 风速持续总时间
    duration = models.IntegerField(default=0)
    # 调度成功一次
    schedule_count = models.IntegerField(default=0)
    service_duration = models.IntegerField(default=0)
    choice2 = (
        (0, 'low'),
        (1, 'middle'),
        (2, 'high'),
    )
    sp_mode = models.IntegerField(choices=choice2)
    # 通过delta_cost
    cost = models.FloatField(default=0.0)


def get_current_ticket(room_id, phone_num) -> Ticket:
    tickets = list(Ticket.objects.filter(room_id=room_id, phone_num=phone_num))
    return tickets[-1]


def create_new_ticket(room_id, phone_num, sp_mode) -> Ticket:
    length = Ticket.objects.filter(room_id=room_id, phone_num=phone_num).count()
    ticket = Ticket.objects.create(room_id=room_id, phone_num=phone_num, ticket_id=length+1,
                                   start_time=datetime.datetime.now(), sp_mode=sp_mode)
    return ticket


class StatisicDay(models.Model):
    room_id = models.CharField(max_length=20)
    date = models.DateField()
    # 开关机加上
    oc_count = models.IntegerField(default=0)
    # 最常用温度
    common_temp = models.IntegerField(default=26)
    # 最常用风速
    choice = (
        (0, 'low'),
        (1, 'middle'),
        (2, 'high'),
    )
    common_spd = models.IntegerField(choices=choice, default=1)
    # 达到目标温度次数
    achieve_count = models.IntegerField(default=0)
    # 被调度次数
    schedule_count = models.IntegerField(default=0)
    # 详单数量
    ticket_count = models.IntegerField(default=0)
    # 总费用
    total_cost = models.FloatField(default=0)


class Record(models.Model):
    room_id = models.CharField(max_length=20)
    record_type = models.CharField(max_length=20)
    # 如果是调目标温度
    at_time = models.DateTimeField(null=True)
    duration = models.IntegerField(null=True)
    goal_temp = models.IntegerField(null=True)


def get_current_record(room_id, record_type) -> Record:
    rs = list(Record.objects.filter(room_id=room_id, record_type=record_type))
    return rs[-1]