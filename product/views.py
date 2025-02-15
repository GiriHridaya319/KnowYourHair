from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from hairfallprediction.models import Product


class ProductListView(ListView):
    model = Product
    template_name = 'product/product_page.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'

    def get_object(self):
        return get_object_or_404(Product, name=self.kwargs['slug'])


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'description','image','price','stock']
    template_name = 'product/product_add_form.html'

    def form_valid(self, form):  # setting the form author to the current logged in user
        form.instance.author = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin,  UpdateView):
    model = Product
    fields = ['name', 'description','image','price','stock']

    def form_valid(self, form):  # setting the form author to the current logged in user
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):  # UserPassesTestMixin - to check if the current user is the author of the post
        post = self.get_object()  # get the post trying to update
        if self.request.user == post.author:  # check if the current user is the author of the post
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = '/'  # redirect to product page after deleting the product

    def test_func(self):  # UserPassesTestMixin - to check if the current user is the author of the post
        post = self.get_object()  # get the post trying to update
        if self.request.user == post.author:  # check if the current user is the author of the post
            return True
        return False
