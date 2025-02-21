from django.contrib import messages
from django.shortcuts import render
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

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'Pending'  # Set initial status as Pending
        return super().form_valid(form)


class ClinicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Clinic
    fields = ['name', 'description', 'image', 'opening_time', 'closing_time', 'phoneNum', 'address']
    template_name = 'clinic/clinic_add_form.html'
    success_url = '/'

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
    template_name = 'clinic/clinic_confirm_delete.html'
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


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


class ClinicBooking(LoginRequiredMixin, CreateView):
    model = BookingClinic
    template_name = 'clinic/clinicBooking.html'
    fields = [
        'first_name',
        'last_name',
        'email',
        'phone',
        'country',
        'clinic',
        'dermatologist',
        'appointment_time',
        'subject',
        'message'
    ]
    success_url = reverse_lazy('booking_success')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add Bootstrap classes and placeholders
        for field_name, field in form.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': field_name
            })

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all approved clinics
        context['clinics'] = Clinic.objects.filter(status='Approved')

        # Get the selected clinic from GET parameters
        selected_clinic = self.request.GET.get('clinic')
        context['selected_clinic'] = selected_clinic

        # Filter dermatologists based on selected clinic
        if selected_clinic:
            context['dermatologists'] = Dermatologist.objects.filter(clinic_id=selected_clinic)
        else:
            context['dermatologists'] = Dermatologist.objects.none()

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'pending'
        return super().form_valid(form)