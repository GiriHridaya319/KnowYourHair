from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from hairfallprediction.models import Product
from product import models
from product.models import OrderDetail, Order


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
        form.instance.status = 'Pending'
        return super().form_valid(form)

    def test_func(self):
        product = self.get_object()
        if self.request.user == product.author or self.request.user.is_superuser:
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = '/product'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser:
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


# order and payment

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty")
        return redirect('KnowYourHair-product')

    cart_items = []
    total = Decimal('0.00')

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id, status='Approved')

        # Validate stock availability
        if item['quantity'] > product.stock:
            messages.error(request, f"Not enough stock for {product.name}. Available: {product.stock}")
            return redirect('cart_detail')

        subtotal = Decimal(item['price']) * item['quantity']
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': Decimal(item['price']),
            'subtotal': subtotal
        })
        total += subtotal

    return render(request, 'product/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def order_review(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        if not cart:
            messages.warning(request, "Your cart is empty")
            return redirect('KnowYourHair-product')

        # Get shipping information from form
        shipping_address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        # Process cart items
        cart_items = []
        total = Decimal('0.00')

        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id, status='Approved')

            # Final stock validation
            if item['quantity'] > product.stock:
                messages.error(request, f"Not enough stock for {product.name}. Available: {product.stock}")
                return redirect('cart_detail')

            subtotal = Decimal(item['price']) * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': Decimal(item['price']),
                'subtotal': subtotal
            })
            total += subtotal

        # Save shipping info in session for order creation
        request.session['shipping_info'] = {
            'address': shipping_address,
            'phone': phone,
            'first_name': first_name,
            'last_name': last_name,
        }

        return render(request, 'product/order_review.html', {
            'cart_items': cart_items,
            'total': total,
            'shipping_address': shipping_address,
            'phone': phone,
            'first_name': first_name,
            'last_name': last_name
        })

    return redirect('checkout')


@login_required
def create_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        shipping_info = request.session.get('shipping_info', {})

        if not cart or not shipping_info:
            messages.warning(request, "Your cart is empty or shipping information is missing")
            return redirect('cart_detail')

        # Calculate total
        total_amount = Decimal('0.00')
        for product_id, item in cart.items():
            subtotal = Decimal(item['price']) * item['quantity']
            total_amount += subtotal

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status='Pending',
            shipping_address=shipping_info.get('address', ''),
            phone=shipping_info.get('phone', '')
        )

        # Create order details and update stock
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id, status='Approved')

            # Final stock check
            if item['quantity'] > product.stock:
                # Delete the created order if stock is insufficient
                order.delete()
                messages.error(request, f"Not enough stock for {product.name}. Available: {product.stock}")
                return redirect('cart_detail')

            # Create order detail
            OrderDetail.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=Decimal(item['price'])
            )

            # Update product stock
            product.stock -= item['quantity']
            product.save()

        # Clear cart and shipping info from session
        request.session['cart'] = {}
        if 'shipping_info' in request.session:
            del request.session['shipping_info']

        # Save order ID in session for payment processing
        request.session['pending_order_id'] = order.id

        return redirect('payment_process')

    return redirect('checkout')




@login_required
def payment_process(request):
    # Get order ID from session
    order_id = request.session.get('pending_order_id')

    if not order_id:
        messages.error(request, "No pending order found")
        return redirect('KnowYourHair-product')

    # Get the order object
    order = get_object_or_404(Order, id=order_id, user=request.user, status='Pending')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'cancel':
            # Redirect to cancel order page
            return redirect('cancel_order', order_id=order.id)

        elif action == 'update':
            # Redirect to update order page
            return redirect('update_order', order_id=order.id)

        elif action == 'pay':
            # Process payment with selected wallet
            wallet = request.POST.get('wallet', 'esewa')

            # In a real implementation, you would redirect to the payment gateway here
            # For now, we'll simulate a successful payment

            # Update order status
            order.status = 'Processing'
            order.save()

            # Clear the pending order ID from session
            if 'pending_order_id' in request.session:
                del request.session['pending_order_id']

            messages.success(request,
                             f"Payment successful with {wallet.capitalize()}. Your order is now being processed.")
            return redirect('order_details', order_id=order.id)

    # For GET request, display payment page with order details
    return render(request, 'product/payment_process.html', {
        'order': order,
        'total': order.total_amount,
        'order_id': f'ORD-{order.id}'
    })


@login_required
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'Pending':
        messages.error(request, "Only pending orders can be updated.")
        return redirect('order_details', order_id=order.id)

    order_items = list(order.order_details.select_related('product'))

    if request.method == 'POST':
        updated = False
        order_total = Decimal('0.00')

        for item in order_items:
            new_quantity = request.POST.get(f'quantity_{item.id}')
            if new_quantity is None:
                continue  # Skip if quantity isn't provided

            try:
                new_quantity = int(new_quantity)

                if new_quantity == item.quantity:
                    order_total += item.subtotal
                    continue  # No change, move to the next item

                if new_quantity <= 0:
                    # Restore stock and delete item
                    item.product.stock += item.quantity
                    item.product.save()
                    item.delete()
                    updated = True
                    continue

                # Handle stock availability
                stock_difference = new_quantity - item.quantity
                if stock_difference > 0 and stock_difference > item.product.stock:
                    messages.error(request, f"Not enough stock for {item.product.name}. Available: {item.product.stock}")
                    return redirect('update_order', order_id=order.id)

                # Update stock and item quantity
                item.product.stock -= stock_difference
                item.product.save()

                item.quantity = new_quantity
                item.save()
                order_total += item.subtotal
                updated = True

            except ValueError:
                messages.error(request, "Invalid quantity entered.")
                return redirect('update_order', order_id=order.id)

        # Update order total or delete if empty
        if order.order_details.exists():
            if updated:
                order.total_amount = order_total
                order.save()
                messages.success(request, "Order updated successfully.")
        else:
            order.delete()
            messages.info(request, "Order cancelled as all items were removed.")
            return redirect('my_orders')

        return redirect('order_details', order_id=order.id)

    return render(request, 'product/update_order.html', {'order': order, 'order_items': order_items})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'Pending':
        messages.error(request, "Only pending orders can be cancelled.")
        return redirect('order_details', order_id=order.id)

    if request.method == 'POST':
        # Use `bulk_update` for better performance
        for item in order.order_details.all():
            item.product.stock += item.quantity
            item.product.save()

        order.delete()
        messages.success(request, "Order cancelled successfully.")
        return redirect('my_orders')

    return render(request, 'product/confirm_cancel_order.html', {'order': order})


@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_details = list(order.order_details.all())  # Fetch once, reuse

    if request.method == 'POST' and 'confirm' in request.POST:
        if order.status == 'Pending':
            order.status = 'Processing'
            order.save()
            messages.success(request, "Order confirmed and is now being processed.")
            return redirect('payment_process', order_id=order.id)

    return render(request, 'product/order_details.html', {
        'order': order,
        'order_details': order_details
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'product/my_orders.html', {'orders': orders})
