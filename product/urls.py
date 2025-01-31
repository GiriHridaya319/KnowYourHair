from django.urls import path
from django.conf.urls.static import static

from KnowYourHair import settings
from . import views
from .views import PostUpdateView, PostDeleteView, PostCreateView, ProductListView,\
    Product, ProductDetailView   # PostListView is the class created in views

# home is the function created in views
urlpatterns = [
    path('', ProductListView.as_view(), name='KnowYourHair-product'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='product-delete'),
    path('post/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('post/new/', PostCreateView.as_view(), name='product-create'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='product-update'),
]

# if the project is in development mode, then add the following line to the urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
