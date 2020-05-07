from django.db import models

# Create your models here.
class Customer(models.Model):
    Name = models.CharField(max_length=50)
    RoomId = models.IntegerField()