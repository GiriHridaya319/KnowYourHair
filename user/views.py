from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
from .models import Agent, Customer


def register(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        image = request.FILES.get('image')
        email = request.POST['email']
        gender = request.POST['gender']
        phone_number = request.POST.get('phone_number', '')
        address = request.POST.get('address', '')
        age = request.POST.get('age', '')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('registration')

        hashed_password = make_password(password)

        if user_type == 'customer':
            customer = Customer(username=username, password=hashed_password, image=image, email=email, age=age, gender=gender, phone_number=phone_number)
            customer.save()
            messages.success(request, "Customer registered successfully! Please log in.")
        elif user_type == 'agent':
            agent = Agent(username=username, password=hashed_password, image=image, email=email, phone=phone_number, address=address, gender=gender)
            agent.save()
            messages.success(request, "Agent registered successfully! Please log in.")

        return redirect('login')

    return render(request, 'user/register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            agent = Agent.objects.get(username=username)
            if check_password(password, agent.password):
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials for Agent'})
        except Agent.DoesNotExist:
            try:
                customer = Customer.objects.get(username=username)
                if check_password(password, customer.password):
                    return redirect('home')
                else:
                    return render(request, 'login.html', {'error': 'Invalid credentials for Customer'})
            except Customer.DoesNotExist:
                return render(request, 'login.html', {'error': 'User not found'})

    return render(request, 'user/login.html')


def custom_logout(request):
    logout(request)
    return redirect('login')
