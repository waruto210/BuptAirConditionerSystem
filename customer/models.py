from django.db import models

# Create your models here.
class Customer(models.Model):
    Name = models.CharField(max_length=50)
    RoomId = models.CharField(max_length=20)

class State(models.Model):
    RoomId = models.CharField(max_length=20)
    Mode = models.CharField(max_length=10)
    Speed = models.CharField(max_length=10)
    GoalTemp = models.IntegerField()
    CurrTemp = models.IntegerField()
    Cost = models.FloatField()
