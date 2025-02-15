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
    # Put exact matches first
    path('', ProductListView.as_view(), name='KnowYourHair-product'),
    path('product/new/', ProductCreateView.as_view(), name='product-create'),  # Move this before the slug pattern
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    # Put the slug pattern last since it's the most general
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)