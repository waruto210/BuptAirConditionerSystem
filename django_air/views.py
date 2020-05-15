from django.shortcuts import render, HttpResponse, redirect
import time
from django.contrib import auth
from django.contrib.auth.decorators import login_required

def login(request):
    if request.method == 'GET':
        return render(request, "login.html")
    elif request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        print(email, password)
        if email != None and password != None:
            user = auth.authenticate(username=email, password=password)
            print(user)
            if user:
                if user.user_type == 1:
                    return render(request, 'manager/index.html', {'user': user})
                elif user.user_type == 2:
                    return render(request, 'adm/index.html', {'user': user})
                elif user.user_type == 3:
                    return render(request, 'director/index.html', {'user': user})
    return HttpResponse(request, 'request error')

@login_required(login_url="/login")
def logout(request):
    auth.logout(request)
    return redirect("/login")
                     
