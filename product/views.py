from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from hairfallprediction.models import Product



def ProductSearch(request):
    products = Product.objects.all()  # Default queryset for all products

    if request.method == 'POST':
        searched = request.POST.get('searched', '').strip()
        sort_name = request.POST.get('sort_name', '')
        sort_price = request.POST.get('sort_price', '')

        # Handle empty search with sorting
        if not searched and (sort_name or sort_price):
            # Apply sorting to all products
            if sort_name:
                products = products.order_by('name' if sort_name == 'asc' else '-name')
            elif sort_price:
                products = products.order_by('cost' if sort_price == 'low' else '-cost')

            return render(request, 'product/product_page.html', {
                'products': products,
                'sort_name': sort_name,
                'sort_price': sort_price
            })

        # Handle empty search without sorting
        if not searched:
            messages.error(request, 'Please enter a valid search')
            return render(request, 'product/product_page.html', {})

        # Case-insensitive search using icontains
        search_results = Product.objects.filter(name__icontains=searched)

        # Apply sorting to search results
        if sort_name:
            search_results = search_results.order_by('name' if sort_name == 'asc' else '-name')
        elif sort_price:
            search_results = search_results.order_by('cost' if sort_price == 'low' else '-cost')

        if not search_results.exists():
            messages.error(request, 'No products found')
            return render(request, 'product/product_page.html', {})

        return render(request, 'product/product_page.html', {
            'searched': search_results,
            'products': products,
            'searched_term': searched,
            'sort_name': sort_name,
            'sort_price': sort_price
        })

    # Handle GET requests - add sorting for initial page load
    sort_name = request.GET.get('sort_name', '')
    sort_price = request.GET.get('sort_price', '')

    if sort_name:
        products = products.order_by('name' if sort_name == 'asc' else '-name')
    elif sort_price:
        products = products.order_by('cost' if sort_price == 'low' else '-cost')

    return render(request, 'product/product_page.html', {
        'products': products,
        'sort_name': sort_name,
        'sort_price': sort_price
    })


class ProductListView(ListView):
    model = Product
    template_name = 'product/product_page.html'
    context_object_name = 'products'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_name = self.request.GET.get('sort_name', '')
        sort_price = self.request.GET.get('sort_price', '')

        if sort_name:
            queryset = queryset.order_by('name' if sort_name == 'asc' else '-name')
        elif sort_price:
            queryset = queryset.order_by('cost' if sort_price == 'low' else '-cost')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_name'] = self.request.GET.get('sort_name', '')
        context['sort_price'] = self.request.GET.get('sort_price', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'

    def get_object(self):
        return get_object_or_404(Product, name=self.kwargs['slug'])


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'product/productadd.html'
    fields = ['name', 'cost', 'feedback', 'details', 'image', 'stock']
    success_url = reverse_lazy('KnowYourHair-product')  # Redirect to list view after creation

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin,  UpdateView):
    model = Product
    fields = ['name', 'cost', 'feedback', 'details', 'image', 'stock']
    template_name = 'product/productadd.html'

    def form_valid(self, form):  # setting the form author to the current logged in user
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):  # UserPassesTestMixin - to check if the current user is the author of the post
        product = self.get_object()  # get the post trying to update
        if self.request.user == product.author:  # check if the current user is the author of the post
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = '/product'  # redirect to product page after deleting the product

    def test_func(self):  # UserPassesTestMixin - to check if the current user is the author of the post
        post = self.get_object()  # get the post trying to update
        if self.request.user == post.author:  # check if the current user is the author of the post
            return True
        return False
