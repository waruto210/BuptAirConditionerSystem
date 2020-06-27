from django.db import models
from customer.models import Customer, State, init_state
from record_manager.RecordManager import RecordManager
import datetime
# Create your models here.


class Bill(models.Model):
    room_id = models.CharField(max_length=20)
    phone_num = models.CharField(max_length=20)
    checkin_date = models.DateTimeField()
    checkout_date = models.DateTimeField()
    total_cost = models.FloatField(default=0.)
    total_use = models.IntegerField(default=0)


def create_bill(room_id,phone_num) -> Bill:
    customer = Customer.objects.get(RoomId=room_id,PhoneNum=phone_num)
    customer.CheckoutDate=datetime.datetime.now()
    bill = Bill.objects.create(room_id=customer.RoomId,
                               phone_num=customer.PhoneNum,
                               checkin_date=customer.CheckinDate,
                               checkout_date=customer.CheckoutDate
                               )
    bill.total_cost, bill.total_use = RecordManager.calc_bill(bill.room_id,bill.phone_num,bill.checkin_date)
    customer.delete()
    state = State.objects.get(room_id=room_id)
    init_state(state)
    state.save()
    bill.save()
    return bill

def get_customer(room_id) -> bool:
    try:
        Customer.objects.get(RoomId=room_id)
        return True
    except:
        return False
def create_customer(room_id, name, phone_num) -> Customer:
    customer = Customer.objects.create(RoomId=room_id,Name=name,PhoneNum=phone_num,CheckinDate=datetime.datetime.now())
    customer.save()
    return customer


def get_tickets(room_id,phone_num,checkin_date):
    return RecordManager.get_tickets(room_id, phone_num,checkin_date)

