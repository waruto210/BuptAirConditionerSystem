from django.db import models


# Create your models here.
class Customer(models.Model):
    Name = models.CharField(max_length=50)
    RoomId = models.CharField(max_length=20)

    def __str__(self):
        return "房间号: " + self.RoomId + "   " + self.Name


class State(models.Model):
    room_id = models.CharField(max_length=20, primary_key=True)
    # RoomId = models.ForeignKey('Customer',on_delete=models.CASCADE)
    is_on = models.BooleanField(null=True)
    is_work = models.BooleanField(null=True)
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
    total_cost = models.FloatField(null=True)


class Ticket(models.Model):
    room_id = models.CharField(max_length=20)
    # user_id = models.UUIDField()
    ticket_id = models.IntegerField()

    # 开机 换风速
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # 调度成功一次
    schedule_count = models.IntegerField(default=0)
    choice2 = (
        (0, 'low'),
        (1, 'middle'),
        (2, 'high'),
    )
    sp_mode = models.IntegerField(choices=choice2, null=True)
    # 通过delta_cost
    cost = models.FloatField(default=0.0)


class StatisicDay(models.Model):
    room_id = models.CharField(max_length=20)
    date = models.DateField()
    # 开关机加上
    oc_count = models.IntegerField(default=0)
    # 调度成功一次加30s吧
    total_hours = models.IntegerField(default=0)
    total_minites = models.FloatField(default=0)
    total_ses = models.IntegerField(default=0)
    schedule_count = models.IntegerField(default=0)

    # 通过delta_cost加上
    total_cost = models.FloatField(default=0.0)
    # 在处理request统计
    ticket_count = models.IntegerField(default=0)
    ct_count = models.IntegerField(default=0)
    cs_count = models.IntegerField(default=0)


class TicketCount(models.Model):
    room_id = models.CharField(max_length=20)
    # user_id = models.CharField(max_length=20)
    ticket_count = models.IntegerField(default=0)