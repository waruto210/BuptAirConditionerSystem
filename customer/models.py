from django.db import models

# Create your models here.
class Customer(models.Model):
    Name = models.CharField(max_length=50)
    RoomId = models.CharField(max_length=20)

class State(models.Model):
    room_id = models.CharField(max_length=20, primary_key=True)
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
