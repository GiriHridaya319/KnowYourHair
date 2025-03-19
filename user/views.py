import csv
from datetime import datetime

from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, admin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, TemplateView, DeleteView

from product.models import Payment, Order, OrderDetail
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, Agent, Customer
from hairfallprediction.models import Product
from clinic.models import Clinic, BookingClinic, Dermatologist


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

        # Form validation
        has_error = False

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            has_error = True

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            has_error = True

        # Validate phone number (10 digits)
        if phone_number and (not phone_number.isdigit() or len(phone_number) != 10):
            messages.error(request, "Phone number must be 10 digits!")
            has_error = True

        # Validate age (between 18 and 100)
        try:
            age_int = int(age)
            if age_int < 18 or age_int > 100:
                messages.error(request, "Age must be between 18 and 100!")
                has_error = True
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid age!")
            has_error = True

        # Validate image file type
        if image and not image == 'default_user.jpg':
            # Get the file extension
            file_extension = image.name.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png']:
                messages.error(request, "Image must be in JPG, JPEG, or PNG format!")
                has_error = True

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            has_error = True

        # If there are validation errors, redirect back to the registration page
        if has_error:
            return redirect('registration')

        # Set default image if none provided
        if image is None:
            image = 'default_user.jpg'

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
            customer = Customer(profile=profile, role='customer')
            customer.save()
            messages.success(request, "Customer registered successfully! Please log in.")
            return redirect('login')
        elif user_type == 'agent':
            agent = Agent(profile=profile, role='staff', status='pending')
            agent.save()
            return redirect('pending_approval')

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
            # Check if the user is an agent with pending approval
            try:
                agent = Agent.objects.get(profile__user=user)
                if agent.status == 'pending':
                    messages.warning(request,
                                     "Your agent account is pending approval. Please wait for admin confirmation.")
                    return redirect('pending_approval')
                elif agent.status == 'rejected':
                    messages.error(request, "Your agent registration was rejected. Please contact admin.")
                    return redirect('login')
                # If approved, continue with login
            except Agent.DoesNotExist:
                # Not an agent
                pass

            login(request, user)  # Ensure user object is passed
            messages.success(request, "Login successful!")
            return redirect('KnowYourHair-home')  # Redirect to the home page after successful login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')  # Stay on the login page if authentication fails

    return render(request, 'user/login.html')


def pending_approval(request):
    """View for agents to see their pending status"""
    return render(request, 'user/pending_approval.html')


# Admin view to see all pending agent requests
@user_passes_test(lambda u: u.is_staff)
def agent_approval_list(request):
    pending_agents = Agent.objects.filter(status='pending')
    return render(request, 'user/agent_approval_list.html', {
        'pending_agents': pending_agents
    })


# Admin action to approve an agent
@user_passes_test(lambda u: u.is_staff)
def approve_agent(request, pk):
    agent = get_object_or_404(Agent, pk=pk)
    agent.status = 'approved'
    agent.approved_at = timezone.now()
    agent.save()
    messages.success(request, f"Agent {agent.profile.user.username} has been approved.")
    return redirect('agent_approval_list')


# Admin action to reject an agent
@user_passes_test(lambda u: u.is_staff)
def reject_agent(request, pk):
    agent = get_object_or_404(Agent, pk=pk)
    agent.status = 'rejected'
    agent.save()
    messages.success(request, f"Agent {agent.profile.user.username} has been rejected.")
    return redirect('agent_approval_list')


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
            messages.success(request, 'Your account has been updated successfully!')

            # Check the user's role and redirect accordingly
            user_role = request.user.profile.role  #

            if user_role == "staff":  # Agent role
                return redirect('agent-profile')
            else:
                return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'user/profile.html', context)  # Default render


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


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'user/profile_confirm_delete.html'
    success_url = reverse_lazy('login')

    def test_func(self):
        """Verify that users can only delete their own accounts"""
        user = self.get_object()
        return self.request.user == user

    def post(self, request, *args, **kwargs):
        """Handle the post request with password verification"""
        try:
            password = request.POST.get('password')
            user = self.get_object()

            # Verify password
            if not password:
                messages.error(request, 'Password is required to delete your account.')
                return redirect('profile')

            if not check_password(password, user.password):
                messages.error(request, 'Invalid password. Account deletion failed.')
                return redirect('profile')

            # If password is correct, proceed with deletion
            if user == request.user:
                # Delete user account
                response = super().delete(request, *args, **kwargs)

                # Log out the user
                logout(request)

                messages.success(request, 'Your account has been successfully deleted.')
                return response

        except Exception as e:
            messages.error(request, 'An error occurred while deleting your account. Please try again.')
            return redirect('profile')

    def handle_no_permission(self):
        """Handle unauthorized access attempts"""
        messages.error(self.request, 'You do not have permission to delete this account.')
        return redirect('profile')

    def get_context_data(self, **kwargs):
        """Add additional context data for the template"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Account'
        return context


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


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'user/adminDashBoard.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all agents with their profiles and users
        agents = Agent.objects.select_related('profile', 'profile__user').all()
        context['agents'] = [{
            'id': agent.id,
            'username': agent.profile.user.username,
            'email': agent.profile.user.email,
            'phone': agent.profile.phone_number,
            'address': agent.profile.address,
            'gender': agent.profile.gender,
            'image': agent.profile.image.url,
        } for agent in agents]

        # Get all customers with their profiles and users
        customers = Customer.objects.select_related('profile', 'profile__user').all()
        context['customers'] = [{
            'id': customer.id,
            'username': customer.profile.user.username,
            'email': customer.profile.user.email,
            'phone': customer.profile.phone_number,
            'address': customer.profile.address,
            'gender': customer.profile.gender,
            'image': customer.profile.image.url,
        } for customer in customers]

        products = Product.objects.select_related('author').all()
        context['products'] = [{
            'id': product.id,
            'name': product.name,
            'cost': product.cost,
            'stock': product.stock,
            'status': product.status,
            'author': product.author.username,
            'feedback': product.feedback,
            'details': product.details,
            'image': product.image.url if product.image else None
        } for product in products]

        # Get all clinics
        clinics = Clinic.objects.select_related('author').all()
        context['clinics'] = [{
            'id': clinic.id,
            'name': clinic.name,
            'address': clinic.address,
            'description': clinic.description,
            'opening_time': clinic.opening_time,
            'closing_time': clinic.closing_time,
            'phoneNum': clinic.phoneNum,
            'status': clinic.status,
            'author': clinic.author.username,
            'image': clinic.image.url if clinic.image else None
        } for clinic in clinics]

        # Get pending approvals
        context['approvals'] = []

        # Add pending products
        pending_products = Product.objects.filter(status='Pending')
        for product in pending_products:
            context['approvals'].append({
                'id': product.id,
                'name': product.name,
                'cost': product.cost,
                'stock': product.stock,
                'status': product.status,
                'author': product.author.username,
                'feedback': product.feedback,
                'details': product.details,
                'image': product.image.url if product.image else None
            })

        # Add pending clinics
        pending_clinics = Clinic.objects.filter(status='Pending')
        for clinic in pending_clinics:
            context['approvals'].append({
                'id': clinic.id,
                'name': clinic.name,
                'address': clinic.address,
                'description': clinic.description,
                'opening_time': clinic.opening_time,
                'closing_time': clinic.closing_time,
                'phoneNum': clinic.phoneNum,
                'status': clinic.status,
                'author': clinic.author.username,
                'image': clinic.image.url if clinic.image else None
            })

        return context


@login_required
def agent_dashboard(request):
    """
    Agent dashboard showing products, clinics, dermatologists, and bookings
    created by the logged-in user.
    """
    # Get products authored by the current user
    products = Product.objects.filter(author=request.user)

    # Get clinics authored by the current user
    clinics = Clinic.objects.filter(author=request.user)

    # Get dermatologists from all clinics owned by the current user
    # First get all clinics IDs owned by the user
    clinic_ids = clinics.values_list('id', flat=True)

    # Then get all dermatologists for these clinics
    dermatologists = Dermatologist.objects.filter(clinic_id__in=clinic_ids)

    # Get all bookings for these clinics
    bookings = BookingClinic.objects.filter(clinic_id__in=clinic_ids)

    context = {
        'products': products,
        'clinics': clinics,
        'dermatologists': dermatologists,
        'bookings': bookings
    }

    return render(request, 'user/agentDetails.html', context)


class UserBookingView(LoginRequiredMixin, TemplateView):
    template_name = 'user/user_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filter bookings for the currently logged-in user
        context['bookings'] = BookingClinic.objects.filter(
            user=self.request.user  # This filters for the logged-in user
        ).select_related('dermatologist', 'clinic').order_by('-appointment_time')  # Added - for newest first

        return context


@login_required
def approve_booking(request, pk):
    booking = get_object_or_404(BookingClinic, pk=pk)

    # Check if user is authorized to approve this booking
    if request.user != booking.clinic.author:
        messages.error(request, "You don't have permission to approve this booking.")
        return redirect('agentDetails')

    # Update the booking status to confirmed
    booking.status = 'confirmed'
    booking.save()

    messages.success(request, f"Booking #{booking.id} has been confirmed successfully.")
    return redirect('agentDetails')


@login_required
def reject_booking(request, pk):
    booking = get_object_or_404(BookingClinic, pk=pk)

    # Check if user is authorized to reject this booking
    if request.user != booking.clinic.author:
        messages.error(request, "You don't have permission to reject this booking.")
        return redirect('agentDetails')

    # Update the booking status to cancelled
    booking.status = 'cancelled'
    booking.save()

    messages.success(request, f"Booking #{booking.id} has been cancelled.")
    return redirect('agentDetails')  # Or redirect to the bookings


@login_required
def approve_clinic(request, pk):
    clinic = get_object_or_404(Clinic, pk=pk)

    # Update the booking status to confirmed
    clinic.status = 'Approved'
    clinic.save()

    messages.success(request, f"clinic #{clinic.name} has been approved successfully.")
    return redirect('adminDash')


@login_required
def reject_clinic(request, pk):
    clinic = get_object_or_404(Clinic, pk=pk)

    # Update the booking status to confirmed
    clinic.status = 'Rejected'
    clinic.save()

    messages.success(request, f"clinic #{clinic.name} has been Rejected successfully.")
    return redirect('adminDash')


@login_required
def approve_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Update the booking status to confirmed
    product.status = 'Approved'
    product.save()

    messages.success(request, f"product #{product.name} has been approved successfully.")
    return redirect('adminDash')


@login_required
def reject_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Update the booking status to confirmed
    product.status = 'Rejected'
    product.save()

    messages.success(request, f"product #{product.name} has been Rejected successfully.")
    return redirect('adminDash')


def is_agent(user):
    """Helper function to check if user is an agent"""
    return user.is_authenticated and hasattr(user, 'profile') and hasattr(user.profile, 'agent')




@login_required
@user_passes_test(is_agent)
def payment_detail(request, payment_id):
    """View payment details for a specific payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    order = payment.order

    # Check if the agent has products in this order
    agent_products_in_order = OrderDetail.objects.filter(
        order=order,
        product__author=request.user
    ).exists()

    if not agent_products_in_order:
        return render(request, 'user/access_denied.html', {
            'message': 'You do not have any products in this order.'
        })

    # Get other payments for this order
    related_payments = Payment.objects.filter(order=order).exclude(id=payment_id)

    # Get agent's items in this order
    agent_items = OrderDetail.objects.filter(
        order=order,
        product__author=request.user
    )

    # Calculate agent's subtotal
    agent_subtotal = agent_items.aggregate(Sum('subtotal'))['subtotal__sum'] or 0



    context = {
        'payment': payment,
        'order': order,
        'related_payments': related_payments,
        'status_choices': Payment.STATUS_CHOICES,
        'agent_items': agent_items,
        'agent_subtotal': agent_subtotal,
    }

    return render(request, 'user/payment_detail.html', context)





@login_required
@user_passes_test(is_agent)
def update_payment_status(request, payment_id):
    """Update payment status if agent has products in the related order"""
    if request.method != 'POST':
        return redirect('agent_payments')

    payment = get_object_or_404(Payment, id=payment_id)
    order = payment.order

    # Check if the agent has products in this order
    agent_products_in_order = OrderDetail.objects.filter(
        order=order,
        product__author=request.user
    ).exists()

    if not agent_products_in_order:
        messages.error(request, "You don't have permission to update this payment.")
        return redirect('agent_payments')

    new_status = request.POST.get('status')
    reason = request.POST.get('reason', '')

    if new_status not in [status[0] for status in Payment.STATUS_CHOICES]:
        messages.error(request, "Invalid status")
        return redirect('payment_detail', payment_id=payment_id)

    # Record the old status for logging
    old_status = payment.status

    if new_status == 'completed':
        payment.mark_as_completed()
        messages.success(request, "Payment marked as completed")
    elif new_status == 'failed':
        payment.mark_as_failed()
        messages.success(request, "Payment marked as failed")
    else:
        payment.status = new_status
        payment.save()
        messages.success(request, f"Payment status updated to {new_status}")

    # Log the status change

    return redirect('payment_detail', payment_id=payment_id)


@login_required
@user_passes_test(is_agent)
def agent_payments_export(request):
    """Export payments to CSV for the agent's orders only"""
    # Get filter parameters
    order_id = request.GET.get('order_id')
    status = request.GET.get('status')
    method = request.GET.get('method')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Get all orders that contain any product by this agent
    agent_orders = Order.objects.filter(
        order_details__product__author=request.user
    ).distinct()

    # Get only payments related to orders containing this agent's products
    payments = Payment.objects.filter(order__in=agent_orders).order_by('-created_at')

    # Apply filters
    if order_id:
        payments = payments.filter(order__id=order_id)

    if status:
        payments = payments.filter(status=status)

    if method:
        payments = payments.filter(payment_method=method)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            payments = payments.filter(created_at__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            date_to = date_to.replace(hour=23, minute=59, second=59)
            payments = payments.filter(created_at__lte=date_to)
        except ValueError:
            pass

    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="agent_payments_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Payment ID', 'Order ID', 'Customer', 'Amount', 'Method', 'Status', 'Transaction ID', 'Date'])

    for payment in payments:
        writer.writerow([
            payment.id,
            payment.order.id,
            payment.order.user.username,
            payment.amount,
            payment.get_payment_method_display(),
            payment.get_status_display(),
            payment.transaction_id or '',
            payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

@login_required
def agent_orders(request):
    """Display all orders containing products by the logged-in agent"""
    # Check if the user is an agent
    try:
        agent_profile = request.user.profile.agent
        if agent_profile.status != 'approved':
            return render(request, 'orders/access_denied.html', {
                'message': 'Your agent account is not approved yet.'
            })
    except (Profile.DoesNotExist, Agent.DoesNotExist, AttributeError):
        return render(request, 'orders/access_denied.html', {
            'message': 'You do not have an agent account.'
        })

    # Get all orders that contain any product by this agent
    agent_orders = Order.objects.filter(
        order_details__product__author=request.user
    ).distinct().order_by('-created_at')

    orders_data = []
    for order in agent_orders:
        # Get only the order details for products by this agent
        agent_items = OrderDetail.objects.filter(
            order=order,
            product__author=request.user
        )

        # Calculate subtotal for just this agent's items
        agent_subtotal = agent_items.aggregate(Sum('subtotal'))['subtotal__sum'] or 0

        orders_data.append({
            'order': order,
            'items': agent_items,
            'agent_subtotal': agent_subtotal
        })

    return render(request, 'user/agent_orders.html', {
        'orders_data': orders_data
    })


@login_required
def agent_order_detail(request, order_id):
    """Display detailed view of a specific order for the agent"""
    # Check if the user is an agent
    try:
        agent_profile = request.user.profile.agent
        if agent_profile.status != 'approved':
            return render(request, 'orders/access_denied.html', {
                'message': 'Your agent account is not approved yet.'
            })
    except (Profile.DoesNotExist, Agent.DoesNotExist, AttributeError):
        return render(request, 'orders/access_denied.html', {
            'message': 'You do not have an agent account.'
        })

    try:
        order = Order.objects.get(id=order_id)

        # Get only items for this agent's products
        agent_items = OrderDetail.objects.filter(
            order=order,
            product__author=request.user
        )

        # If no items belong to this agent, they shouldn't see this order
        if not agent_items.exists():
            return render(request, 'orders/access_denied.html', {
                'message': 'You do not have any products in this order.'
            })

        agent_subtotal = agent_items.aggregate(Sum('subtotal'))['subtotal__sum'] or 0

        # Get payment information
        payments = order.payments.all()

        # Get customer profile information if available
        try:
            customer_profile = order.user.profile
        except Profile.DoesNotExist:
            customer_profile = None

        context = {
            'order': order,
            'agent_items': agent_items,
            'agent_subtotal': agent_subtotal,
            'payments': payments,
            'customer': order.user,
            'customer_profile': customer_profile
        }

        return render(request, 'user/agent_order_detail.html', context)

    except Order.DoesNotExist:
        return render(request, 'user/order_not_found.html')


@login_required
def update_order_status(request, order_id):
    """Allow agent to update status of their items in an order"""
    # Check if the user is an approved agent
    try:
        agent_profile = request.user.profile.agent
        if agent_profile.status != 'approved':
            return render(request, 'user/access_denied.html', {
                'message': 'Your agent account is not approved yet.'
            })
    except (Profile.DoesNotExist, Agent.DoesNotExist, AttributeError):
        return render(request, 'user/access_denied.html', {
            'message': 'You do not have an agent account.'
        })

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in [s[0] for s in Order.STATUS_CHOICES]:
            try:
                order = Order.objects.get(id=order_id)
                # Verify agent has products in this order
                agent_items = order.order_details.filter(product__author=request.user)
                if agent_items.exists():
                    order.status = new_status
                    order.save()
                    return redirect('agent_order_detail', order_id=order.id)
            except Order.DoesNotExist:
                pass

    return redirect('agent_orders')