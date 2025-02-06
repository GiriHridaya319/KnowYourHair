from django.urls import path
from django.conf.urls.static import static
from KnowYourHair import settings
from .views import (
    ProductUpdateView,
    ProductDeleteView,
    ProductCreateView,
    ProductListView,
    ProductDetailView
)

urlpatterns = [
    # Remove 'product/' from the start of these paths since it's already included in main urls.py
    path('', ProductListView.as_view(), name='KnowYourHair-product'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('new/', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)