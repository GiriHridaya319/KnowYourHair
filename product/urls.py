from django.urls import path
from django.conf.urls.static import static

from KnowYourHair import settings
from .views import ProductUpdateView, ProductDeleteView, ProductCreateView, ProductListView,\
    Product, ProductDetailView   # PostListView is the class created in views

# home is the function created in views
urlpatterns = [
    path('', ProductListView.as_view(), name='KnowYourHair-product'),
    path('product/<int:pk>/delete', ProductDeleteView.as_view(), name='product-delete'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('product/new/', ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/update', ProductUpdateView.as_view(), name='product-update'),
]

# if the project is in development mode, then add the following line to the urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
