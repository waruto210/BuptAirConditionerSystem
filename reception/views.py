from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from customer.models import Customer
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
        customer_name = request.POST.get('c_name',None)
        room_id = request.POST.get('r_id',None)
        print(customer_name + ' ' + room_id)
        print(type(Customer))
        customer = Customer.objects.create(RoomId=room_id)

        customer.Name = customer_name
        print(customer_name + ' ' + room_id)
        customer.save()
        if customer:
            return render(request, 'reception/index.html')


@login_required(login_url="/login")
def checkout(request):
    if request.method == 'GET':
        room_id = request.GET.get('room_id')
        customer = Customer.objects.filter(RoomId=room_id)
        print(customer)
        customer.delete()
        return render(request, 'reception/checkout.html')
