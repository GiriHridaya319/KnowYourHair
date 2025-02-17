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
    ProductSearch
)

urlpatterns = [
    path('', ProductListView.as_view(), name='KnowYourHair-product'),
    path('search/', views.ProductSearch, name='product-search'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('new/', ProductCreateView.as_view(), name='product-create'),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)