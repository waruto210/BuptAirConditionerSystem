from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import Manager
from django.contrib import auth
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    if request.method == 'GET':
        return render(request, 'manager/index.html')

def login_manager(request):
    if request.method == 'GET':
        form = Manager()
        return render(request, 'manager/login.html', {'form': form})
    elif request.method == 'POST':
        form = Manager(request.POST)
        print("here")
        if form.is_valid():
            data = form.clean()
            user = auth.authenticate(username=data['username'], password=data['password'])
            # print("use is:", user)
            if user:
                auth.login(request, user)
                return render(request, "manager/index.html", {'user': user})
        else:
            return HttpResponse("error")


@login_required(login_url="/manager/login")
def logout_manager(request):
    auth.logout(request)
    return redirect("/manager/")

@login_required(login_url="/manager/login")
def add(request):
    if request.method == 'GET':
        return render(request, 'manager/add.html')

@login_required(login_url="/manager/login")
def checkout(request):
    if request.method == 'GET':
        return render(request, 'manager/checkout.html')
