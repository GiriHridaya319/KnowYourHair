from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Clinic, Dermatologist, BookingClinic


def ClinicSearch(request):
    # Only get approved clinics
    clinics = Clinic.objects.filter(status='Approved')

    if request.method == 'POST':
        searched = request.POST.get('searched', '').strip()

        if not searched:
            messages.error(request, 'Please enter a valid search')
            return render(request, 'clinic/clinic_page.html', {})

        # Case-insensitive search using icontains, only for approved clinics
        search_results = Clinic.objects.filter(
            name__icontains=searched,
            status='Approved'
        )

        if not search_results.exists():
            messages.error(request, 'No clinic details found')
            return render(request, 'clinic/clinic_page.html', {})

        return render(request, 'clinic/clinic_page.html', {
            'searched': search_results,
            'products': clinics,
            'searched_term': searched
        })

    # Handle GET requests
    return render(request, 'clinic/clinic_page.html', {'products': clinics})


class ClinicListView(ListView):
    model = Clinic
    template_name = 'clinic/clinic_page.html'
    context_object_name = 'clinics'
    paginate_by = 3

    def get_queryset(self):
        # Override queryset to only get approved clinics, ordered by date
        return Clinic.objects.filter(status='Approved').order_by('-date_posted')


class ClinicDetailView(DetailView):
    model = Clinic
    template_name = 'clinic/clinic_detail.html'

    def get_queryset(self):
        # Only allow viewing approved clinic details
        return Clinic.objects.filter(status='Approved')


class ClinicCreateView(LoginRequiredMixin, CreateView):
    model = Clinic
    fields = ['name', 'description', 'image', 'opening_time', 'closing_time', 'phoneNum', 'address']
    template_name = 'clinic/clinic_add_form.html'
    success_url = '/clinic'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'Pending'  # Set initial status as Pending
        return super().form_valid(form)


class ClinicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Clinic
    fields = ['name', 'description', 'image', 'opening_time', 'closing_time', 'phoneNum', 'address']
    template_name = 'clinic/clinic_add_form.html'
    success_url = '/clinic'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'Pending'  # Reset status to Pending after update
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class ClinicDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Clinic
    template_name = 'clinic/confirm_delete.html'  # Use the same common template
    success_url = '/clinic'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'clinic'
        return context


class DermatologistDetailView(DetailView):
    model = Dermatologist
    template_name = 'clinic/dermatologistDetail.html'
    context_object_name = 'dermatologist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context if needed
        context['related_dermatologists'] = Dermatologist.objects.filter(
            clinic=self.object.clinic
        ).exclude(id=self.object.id)[:3]  # Get up to 3 related dermatologists from the same clinic
        return context


class DermatologistListView(TemplateView):
    template_name = 'clinic/dermatologist_page.html'

    def test_func(self):
        return hasattr(self.request.user, 'profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic_id = self.kwargs.get('clinic_id')

        # Get the clinic
        clinic = Clinic.objects.get(id=clinic_id)

        # Add clinic and clinic_id to context
        context['clinic'] = clinic
        context['clinic_id'] = clinic_id

        # Get dermatologists for the specific clinic
        context['dermatologists'] = Dermatologist.objects.filter(clinic_id=clinic_id).select_related('clinic')

        return context


class AllDermatologistListView(ListView):
    model = Dermatologist
    template_name = 'clinic/Dermatologist.html'
    context_object_name = 'dermatologists'
    paginate_by = 6

    def get_queryset(self):
        return Dermatologist.objects.all().select_related('clinic')


class ClinicBookingView(LoginRequiredMixin, CreateView):
    model = BookingClinic
    template_name = 'clinic/clinicBooking.html'
    fields = [
        'first_name',
        'last_name',
        'email',
        'phone',
        'country',
        'dermatologist',
        'appointment_time',
        'subject',
        'message'
    ]
    success_url = 'success/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic_id = self.kwargs.get('clinic_id')  # Get clinic ID from URL

        try:
            clinic = Clinic.objects.get(id=clinic_id)
            context['clinic'] = clinic
            context['dermatologists'] = Dermatologist.objects.filter(clinic_id=clinic_id)
        except Clinic.DoesNotExist:
            context['clinic'] = None
            context['dermatologists'] = []

        return context

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            form.instance.clinic_id = self.kwargs.get('clinic_id')
            form.instance.status = 'pending'
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Booking failed: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please check your form entries.')
        return super().form_invalid(form)


class BookingSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'clinic/booking_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the latest booking for this user
        try:
            context['booking'] = BookingClinic.objects.filter(
                user=self.request.user
            ).latest('id')
        except BookingClinic.DoesNotExist:
            context['booking'] = None
        return context


class DermatologistCreateView(LoginRequiredMixin, CreateView):
    model = Dermatologist
    fields = ['first_name', 'last_name', 'About', 'image', 'phoneNum', 'total_experience']
    template_name = 'clinic/dermatologist_add_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if the clinic exists and belongs to the user
        try:
            self.clinic = Clinic.objects.get(
                id=self.kwargs['clinic_id'],
                author=self.request.user
            )
            return super().dispatch(request, *args, **kwargs)
        except Clinic.DoesNotExist:
            messages.error(self.request, "You don't have permission to add dermatologists to this clinic.")
            return redirect('KnowYourHair-clinic')

    def form_valid(self, form):
        form.instance.clinic = self.clinic
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic'] = self.clinic
        return context


class DermatologistUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Dermatologist
    fields = ['first_name', 'last_name', 'About', 'image', 'phoneNum', 'total_experience']
    template_name = 'clinic/dermatologist_add_form.html'
    success_url = '/'

    def test_func(self):
        dermatologist = self.get_object()
        # Check if the logged-in user owns the clinic this dermatologist belongs to
        return self.request.user == dermatologist.clinic.author

    def form_valid(self, form):
        return super().form_valid(form)


class DermatologistDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Dermatologist
    template_name = 'clinic/confirm_delete.html'  # Use a common template
    success_url = 'clinic/dermatologists'

    def test_func(self):
        dermatologist = self.get_object()
        # Check if the logged-in user owns the clinic this dermatologist belongs to
        return self.request.user == dermatologist.clinic.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'dermatologist'
        return context


