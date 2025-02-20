from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Clinic, Dermatologist


def ClinicSearch(request):
    clinics = Clinic.objects.all()  # Default queryset for all products

    if request.method == 'POST':
        searched = request.POST.get('searched', '').strip()

        if not searched:
            messages.error(request, 'Please enter a valid search')
            return render(request, 'clinic/clinic_page.html', {})

        # Case-insensitive search using icontains
        search_results = Clinic.objects.filter(name__icontains=searched)

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
    ordering = ['-date_posted']
    paginate_by = 3 # - to set newest product first


class ClinicDetailView(DetailView):
    model = Clinic
    template_name = 'clinic/clinic_detail.html'


class ClinicCreateView(LoginRequiredMixin, CreateView):
    model = Clinic
    fields = ['name', 'description','image','opening_time','closing_time', 'phoneNum','address']
    template_name = 'clinic/clinic_add_form.html'

    def form_valid(self, form):  # setting the form author to the current logged in user
        form.instance.author = self.request.user
        return super().form_valid(form)


class ClinicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Clinic
    fields = ['name', 'description','image','opening_time','closing_time', 'phoneNum','address']
    template_name = 'clinic/clinic_add_form.html'  # Add this line
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class ClinicDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Clinic
    template_name = 'clinic/clinic_confirm_delete.html'
    success_url = '/'  # redirect to clinic page after deleting the clinic

    def test_func(self):  # UserPassesTestMixin - to check if the current user is the author of the post
        post = self.get_object()  # get the post trying to update
        if self.request.user == post.author:  # check if the current user is the author of the post
            return True
        return False


class DermatologistListView(ListView):
    model = Dermatologist
    template_name = 'clinic/dermatologist_page.html'
    context_object_name = 'dermatologists'
    ordering = ['-total_experience']


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