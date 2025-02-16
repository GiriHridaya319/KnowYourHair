from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Clinic


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