from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from hairfallprediction.models import Product


def ProductSearch(request):
    # Only get approved products
    products = Product.objects.filter(status='Approved')

    if request.method == 'POST':
        searched = request.POST.get('searched', '').strip()
        sort_name = request.POST.get('sort_name', '')
        sort_price = request.POST.get('sort_price', '')

        # Handle empty search with sorting
        if not searched and (sort_name or sort_price):
            # Apply sorting to approved products
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

        # Case-insensitive search using icontains for approved products only
        search_results = Product.objects.filter(
            name__icontains=searched,
            status='Approved'
        )

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
        # Get base queryset with only approved products
        queryset = super().get_queryset().filter(status='Approved')
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
        # Only allow viewing approved products
        return get_object_or_404(Product, name=self.kwargs['slug'], status='Approved')


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'product/productadd.html'
    fields = ['name', 'cost', 'feedback', 'details', 'image', 'stock']
    success_url = reverse_lazy('KnowYourHair-product')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'Pending'  # Set initial status as Pending
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'cost', 'feedback', 'details', 'image', 'stock']
    template_name = 'product/productadd.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'Pending'  # Reset status to Pending after update
        return super().form_valid(form)

    def test_func(self):
        product = self.get_object()
        if self.request.user == product.author:
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = '/product'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False