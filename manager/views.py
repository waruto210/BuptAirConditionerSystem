from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required(login_url="/login")
def logout_manager(request):
    auth.logout(request)
    return redirect("/login")

@login_required(login_url="/login")
def add(request):
    if request.method == 'GET':
        print(request.user)
        return render(request, 'manager/add.html')

@login_required(login_url="/login")
def checkout(request):
    if request.method == 'GET':
        return render(request, 'manager/checkout.html')
