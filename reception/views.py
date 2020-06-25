from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from customer.models import Customer,State, Ticket
from .models import Bill,create_bill,create_customer,get_tickets
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

# Create your views here.

@login_required(login_url="/login")
def index(request):
    if request.method == 'GET':
        cust_list = Customer.objects.all()
        paginator = Paginator(cust_list, 10, 1)
        page = request.GET.get('page')
        try:
            customer = paginator.page(page)
        except PageNotAnInteger:
            customer = paginator.page(1)
        except EmptyPage:
            customer = paginator.page(paginator.num_pages)
        return render(request, 'reception/index.html', {"cust_list": cust_list})

@login_required(login_url="/login")
def checkin(request):
    if request.method == 'GET':
        print(request.user)
        return render(request, 'reception/checkin.html')
    if request.method == 'POST':
        customer_name = request.POST.get('c_name', None)
        room_id = request.POST.get('r_id', None)
        # room_state = State.objects.get(room_id=room_id)
        # if room_state.busy:
        #     messages.error(request,'房间'+ room_id + '已入住!')
        #     return render(request,'reception/checkin.html')
        phone_num = request.POST.get('phone_num', None)
        print(customer_name + ' ' + room_id)
        customer = create_customer(room_id,customer_name,phone_num)
        if customer:
            # room_state.is_on = True
            # room_state.save()
            context = {"type":"success","message":"入住成功"}
            print(context)
            return render(request,'reception/checkin.html',context=context)


@login_required(login_url="/login")
def checkout(request):
    if request.method == 'GET':
        room_id = request.GET.get('room_id')
        phone_num = request.GET.get('phone_num')
        bill = create_bill(room_id, phone_num)
        bill_context = print_bill(bill)
        ticket_list = get_tickets(room_id,phone_num)
        return render(request, 'reception/checkout.html', context={"bill":bill_context,"tickets":ticket_list})


def print_bill(bill: Bill):
    message = {}
    message["room_id"] = bill.room_id
    message["checkin_date"] = bill.checkin_date
    message["checkout_date"] = bill.checkout_date
    message["total_use"] = bill.total_use
    message["total_cost"] = bill.total_cost
    return message


def print_tickets(tickets):
    message = []
    for ticket in tickets:
        ticket_context = {}
        ticket_context["room_id"] = ticket.room_id
        ticket_context["phone_num"] = ticket.phone_num
        ticket_context["ticket_id"] = ticket.ticket_id
        ticket_context["start_time"] = ticket.start_time
        ticket_context["end_time"] = ticket.end_time
        ticket_context["duration"] = ticket.duration
        ticket_context["start_time"] = ticket.start_time
        ticket_context["schedule_count"] = ticket.schedule_count
        ticket_context["service_duration"] = ticket.service_duration
        if ticket.sp_mode == 0:
            ticket_context["sp_mode"] = "低风"
        elif ticket.sp_mode == 1:
            ticket_context["sp_mode"] = "中风"
        elif ticket.sp_mode == 2:
            ticket_context["sp_mode"] = "强风"
        ticket_context["cost"] = ticket.cost
        message.append(ticket_context)
    return message




