from django.urls import path
from django.conf.urls.static import static
from KnowYourHair import settings
from . import views
from .views import (
    ProductUpdateView,
    ProductDeleteView,
    ProductCreateView,
    ProductListView,
    ProductDetailView,
    ProductSearch,
    EsewaRequestView
)


urlpatterns = [
    path('', ProductListView.as_view(), name='KnowYourHair-product'),
    path('search/', views.ProductSearch, name='product-search'),
    path('new/', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),

    # Cart URLs before the catch-all slug pattern
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/review/', views.order_review, name='order_review'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_details, name='order_details'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/update/', views.update_order, name='update_order'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),

    # Add the payment_process with order_id parameter
    path('order/payment/', views.payment_process, name='payment_process'),
    path('order/payment/<int:order_id>/', views.payment_process, name='payment_process'),
    path('order/<int:order_id>/payment/', views.payment_process, name='payment_process_with_id'),

    path('esewa-request/', views.EsewaRequestView.as_view(), name='esewa_request'),
    path('esewa-success/', views.esewa_success, name='esewa_success'),
    path('esewa-failure/', views.esewa_failure, name='esewa_failure'),

    path('access-denied/', views.access_denied, name='access_denied'),

    # Move the catch-all slug pattern to the end
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)