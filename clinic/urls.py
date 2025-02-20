from django.urls import path
from django.conf.urls.static import static

from KnowYourHair import settings
from . import views
from .views import ClinicUpdateView, ClinicDeleteView, ClinicCreateView, ClinicListView,\
    Clinic, ClinicDetailView, DermatologistListView, DermatologistDetailView

# home is the function created in views
urlpatterns = [
    path('', ClinicListView.as_view(), name='KnowYourHair-clinic'),
    path('dermatologist/', DermatologistListView.as_view(), name='dermatologist-view'),
    path('dermatologist/<int:pk>/', DermatologistDetailView.as_view(), name='dermatologist-detail'),
    path('search/', views.ClinicSearch, name='clinic-search'),
    path('<int:pk>/delete', ClinicDeleteView.as_view(), name='clinic-delete'),
    path('<int:pk>/', ClinicDetailView.as_view(), name='clinic-detail'),
    path('new/', ClinicCreateView.as_view(), name='clinic-create'),
    path('<int:pk>/update', ClinicUpdateView.as_view(), name='clinic-update'),
]

# if the project is in development mode, then add the following line to the urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
