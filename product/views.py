from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
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


# cart and order

def get_cart(request):
    """Get or initialize the cart in session"""
    return request.session.get('cart', {})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, status='Approved')
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, status='Approved')
        cart = get_cart(request)

        # Check stock
        current_quantity = int(cart.get(str(product_id), {}).get('quantity', 0))
        if current_quantity + 1 > product.stock:
            messages.error(request, 'Not enough stock available')
            return redirect('recom-product-detail', slug=product.slug)

        # Add to cart
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': str(product.cost),
                'quantity': 1,
                'image': product.image.url
            }

        request.session['cart'] = cart
        messages.success(request, 'Product added to cart')
        return redirect('cart_detail')  # This should match the URL name

    return redirect('recom-product-detail', slug=product.slug)


@login_required
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, 'Product removed from cart')

    return redirect('cart_detail')


@login_required
def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))

        if quantity < 0:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        product = get_object_or_404(Product, id=product_id, status='Approved')

        # Check stock availability
        if quantity > product.stock:
            return JsonResponse({
                'error': 'Not enough stock available',
                'available_stock': product.stock
            }, status=400)

        cart = get_cart(request)

        if quantity == 0:
            if str(product_id) in cart:
                del cart[str(product_id)]
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': str(product.cost),
                'quantity': quantity,
                'image': product.image.url
            }

        request.session['cart'] = cart

        cart_total = sum(
            Decimal(item['price']) * item['quantity']
            for item in cart.values()
        )

        return JsonResponse({
            'success': True,
            'cart_total': float(cart_total)
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def cart_detail(request):
    cart = get_cart(request)
    cart_items = []
    total = Decimal('0.00')

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id, status='Approved')
        subtotal = Decimal(item['price']) * item['quantity']
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'subtotal': subtotal
        })

    return render(request, 'product/cart.html', {
        'cart_items': cart_items,
        'total': total
    })