import base64
import hashlib
import hmac
import uuid
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from KnowYourHair import settings
from hairfallprediction.models import Product
from product.models import OrderDetail, Order, Payment


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

# Decorator to check if user is a customer
def customer_required(function):
    def check_customer(user):
        # Check if user has a profile with customer role
        return hasattr(user, 'profile') and hasattr(user.profile, 'customer')

    decorated_view = user_passes_test(check_customer, login_url='access_denied')(function)
    return decorated_view


# View for access denied
def access_denied(request):
    messages.error(request, "Access denied. Only customers can perform this action.")
    return redirect('KnowYourHair-product')  # Redirect to home or another appropriate page


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
        phone = request.POST.get('phone', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        postal_code = request.POST.get('postal_code', '')
        city = request.POST.get('city', '')
        address = request.POST.get('address', '')

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
            'address': address,
            'phone': phone,
            'first_name': first_name,
            'last_name': last_name,
            'postal_code': postal_code,
            'city': city

        }

        return render(request, 'product/order_review.html', {
            'cart_items': cart_items,
            'total': total,
            'address': address,
            'phone': phone,
            'first_name': first_name,
            'last_name': last_name,
            'postal_code': postal_code,
            'city': city
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


# Customer check mixin for class-based views
class CustomerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'profile') and hasattr(self.request.user.profile, 'customer')

    def handle_no_permission(self):
        messages.error(self.request, "Access denied. Only customers can perform this action.")
        return redirect('KnowYourHair-product')


@login_required
def payment_process(request, order_id=None):
    # First try to get order_id from the URL parameter
    if order_id is None:
        # If not in URL, fall back to session
        order_id = request.session.get('pending_order_id')

        if not order_id:
            messages.error(request, "No pending order found")
            return redirect('my_orders')

    # Get the order object - ensure it belongs to current user and is still pending
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'Pending':
        messages.warning(request, "This order is no longer pending payment.")
        return redirect('order_details', order_id=order.id)

    # Store the order ID in session for consistency
    request.session['pending_order_id'] = order.id

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'cancel':
            return redirect('cancel_order', order_id=order.id)
        elif action == 'update':
            return redirect('update_order', order_id=order.id)
        elif action == 'pay':
            # Process payment with selected wallet
            payment_method = request.POST.get('wallet', 'esewa')

            # Create a new payment record
            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method=payment_method,
                status='pending'
            )

            # Handle each payment method separately
            if payment_method == 'esewa':
                # Store payment ID in session
                request.session['pending_payment_id'] = payment.id
                return redirect(reverse('esewa_request') + f'?order_id={order.id}')

            elif payment_method == 'khalti':
                # Store payment ID in session
                request.session['pending_payment_id'] = payment.id
                return redirect(reverse('khalti_request') + f'?order_id={order.id}')

            elif payment_method == 'cod':
                # For Cash on Delivery, mark as completed immediately
                payment.mark_as_completed(transaction_id=f"COD-{order.id}")

                # Update order
                order.payment_method = 'cod'
                order.save()

                # Clear session
                if 'pending_order_id' in request.session:
                    del request.session['pending_order_id']

                messages.success(request, "Order placed successfully. Payment on delivery.")
                return redirect('order_details', order_id=order.id)

            else:
                messages.error(request, "Invalid payment method selected")
                payment.mark_as_failed()
                return redirect('payment_process', order_id=order.id)

        else:
            messages.error(request, "Invalid action")
            return redirect('payment_process', order_id=order.id)

    # For GET request, display payment page with order details
    return render(request, 'product/payment_process.html', {
        'order': order,
        'total': order.total_amount,
        'order_id': f'ORD-{order.id}'
    })


class EsewaRequestView(LoginRequiredMixin, TemplateView):
    template_name = 'product/esewa_request.html'

    def get(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id')

        if not order_id:
            messages.error(request, "No order specified for payment")
            return redirect('my_orders')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect('my_orders')

        # Get payment ID from session or create a new one
        payment_id = request.session.get('pending_payment_id')
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id, order=order)
            except Payment.DoesNotExist:
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    payment_method='esewa',
                    status='pending'
                )
        else:
            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method='esewa',
                status='pending'
            )
            request.session['pending_payment_id'] = payment.id

        # Store the order ID in session for the callback
        request.session['pending_order_id'] = order.id

        # Generate a unique transaction UUID
        transaction_uuid = str(uuid.uuid4())

        # Fields to be signed
        total_amount = str(order.total_amount)
        product_code = settings.ESEWA_PRODUCT_CODE

        # Create signature - HMAC-SHA256 encoding
        secret_key = settings.ESEWA_SECRET_KEY
        message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature).decode("utf-8")

        # Success and failure URLs
        success_url = request.build_absolute_uri(reverse('esewa_success'))
        failure_url = request.build_absolute_uri(reverse('esewa_failure'))

        context = {
            'order': order,
            'transaction_uuid': transaction_uuid,
            'product_code': product_code,
            'signature': signature,
            'success_url': success_url,
            'failure_url': failure_url,
            'signed_field_names': 'total_amount,transaction_uuid,product_code'
        }

        return render(request, self.template_name, context)


@login_required
def esewa_success(request):
    # Get the parameters from eSewa callback
    data_param = request.GET.get('data')

    if data_param:
        # Parse the base64 encoded data
        import base64
        import json
        try:
            decoded_data = base64.b64decode(data_param).decode('utf-8')
            data = json.loads(decoded_data)
        except Exception as e:
            messages.error(request, f"Error decoding data: {str(e)}")
            return redirect('my_orders')
    else:
        data = request.GET

    # Extract the relevant data
    transaction_code = data.get('transaction_code')
    status = data.get('status')

    # Get the pending payment ID from session
    payment_id = request.session.get('pending_payment_id')
    order_id = request.session.get('pending_order_id')

    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id)
            order = payment.order
        except Payment.DoesNotExist:
            if order_id:
                # If payment not found but order exists, create a new payment
                try:
                    order = Order.objects.get(id=order_id, user=request.user)
                    payment = Payment.objects.create(
                        order=order,
                        amount=order.total_amount,
                        payment_method='esewa',
                        status='pending'
                    )
                except Order.DoesNotExist:
                    messages.error(request, "Order not found. Please contact support.")
                    return redirect('my_orders')
            else:
                messages.error(request, "Payment information not found. Please contact support.")
                return redirect('my_orders')
    elif order_id:
        # If no payment ID in session but order ID exists
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            # Look for existing payment
            payment = Payment.objects.filter(order=order, payment_method='esewa').first()
            if not payment:
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    payment_method='esewa',
                    status='pending'
                )
        except Order.DoesNotExist:
            messages.error(request, "Order not found. Please contact support.")
            return redirect('my_orders')
    else:
        # No payment or order ID in session
        messages.error(request, "Payment information not found. Please contact support.")
        return redirect('my_orders')

    if status == 'COMPLETE':
        # Mark payment as completed
        payment.mark_as_completed(transaction_id=transaction_code)

        # Update order details
        order.payment_method = 'esewa'
        order.save()

        # Clear the pending order ID from session
        if 'pending_order_id' in request.session:
            del request.session['pending_order_id']
        if 'pending_payment_id' in request.session:
            del request.session['pending_payment_id']

        messages.success(request, "Payment successful! Your order is now being processed.")
    else:
        payment.mark_as_failed()
        messages.error(request, "Payment was not successful. Please try again.")

    return redirect('order_details', order_id=order.id)


@login_required
def esewa_failure(request):
    # Get the pending payment ID from session
    payment_id = request.session.get('pending_payment_id')

    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.mark_as_failed()
            order_id = payment.order.id
        except Payment.DoesNotExist:
            order_id = request.session.get('pending_order_id')
    else:
        order_id = request.session.get('pending_order_id')

    messages.error(request, "Payment was cancelled or failed. Please try again.")

    if order_id:
        return redirect('payment_process', order_id=order_id)
    else:
        return redirect('my_orders')


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
                    messages.error(request,
                                   f"Not enough stock for {item.product.name}. Available: {item.product.stock}")
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