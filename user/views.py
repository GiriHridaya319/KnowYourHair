from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, Agent, Customer


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

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        # Create profile
        profile = Profile.objects.create(
            user=user,
            image=image,
            phone_number=phone_number,
            address=address,
            gender=gender,
            age=age
        )
        profile.save()

        # Create the corresponding model (Agent or Customer)
        if user_type == 'customer':
            customer = Customer(profile=profile, preferences='')
            customer.save()
            messages.success(request, "Customer registered successfully! Please log in.")
        elif user_type == 'agent':
            agent = Agent(profile=profile, specialization='')
            agent.save()
            messages.success(request, "Agent registered successfully! Please log in.")

        return redirect('login')

    return render(request, 'user/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the user exists before authenticating
        if not User.objects.filter(username=username).exists():
            messages.error(request, "User does not exist.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)  # Ensure user object is passed
            messages.success(request, "Login successful!")
            return redirect('KnowYourHair-home')  # Redirect to the home page after successful login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')  # Stay on the login page if authentication fails

    return render(request, 'user/login.html')


def custom_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')  # Redirect to login page after logging out


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated Successfully!')
            return redirect('profile')
    # instance to get the current user information
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'user/profile.html', context)


@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated Successfully!')
            return redirect('profile')
    # instance to get the current user information
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'user/profile_update.html', context)


@login_required
def password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('profile-update')

        user = authenticate(request, username=request.user.username, password=old_password)

        if user:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully!")
            return redirect('profile-update')
        else:
            messages.error(request, "Invalid password!")
            return redirect('profile-update')

    return render(request, 'user/changePassword.html')


def adminDash(request):
    return render(request, 'user/adminDashBoard.html')

