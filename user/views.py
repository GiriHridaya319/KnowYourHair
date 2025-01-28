from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Agent, Customer
from django.contrib.auth import logout


# Register View (for both Agent and Customer)
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

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('registration')

        # Hash the password
        hashed_password = make_password(password)

        # Register Customer or Agent
        if user_type == 'customer':
            customer = Customer(username=username, password=hashed_password, image=image, email=email, age=age, gender=gender, phone_number=phone_number)
            customer.save()
            messages.success(request, "Customer registered successfully! Please log in.")
        elif user_type == 'agent':
            agent = Agent(username=username, password=hashed_password, image=image, email=email, phone=phone_number, address=address, gender=gender)
            agent.save()
            messages.success(request, "Agent registered successfully! Please log in.")

        return redirect('login')  # Redirect to login page after successful registration

    return render(request, 'user/register.html')


# Login View for both Agent and Customer
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the user is an Agent
        try:
            agent = Agent.objects.get(username=username)
            if check_password(password, agent.password):
                return redirect('KnowYourHair-home')  # Redirect to agent dashboard
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials for Agent'})
        except Agent.DoesNotExist:
            # Check if the user is a Customer
            try:
                customer = Customer.objects.get(username=username)
                if check_password(password, customer.password):
                    return redirect('KnowYourHair-home')  # Redirect to customer dashboard
                else:
                    return render(request, 'login.html', {'error': 'Invalid credentials for Customer'})
            except Customer.DoesNotExist:
                return render(request, 'login.html', {'error': 'User not found'})

    return render(request, 'user/login.html')


# Logout View
def custom_logout(request):
    logout(request)
    return redirect('KnowYourHair-login')
