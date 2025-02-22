from django.urls import path
from django.conf.urls.static import static

from KnowYourHair import settings
from . import views
from .views import (
    ClinicUpdateView,
    ClinicDeleteView,
    ClinicCreateView,
    ClinicListView,
    Clinic,
    ClinicDetailView,
    DermatologistListView,
    DermatologistDetailView,
    AllDermatologistListView,
    ClinicBookingView,
    BookingSuccessView
)

urlpatterns = [
    path('', ClinicListView.as_view(), name='KnowYourHair-clinic'),
    path('<int:clinic_id>/dermatologists/', DermatologistListView.as_view(), name='dermatologist-views'),
    path('dermatologists/', AllDermatologistListView.as_view(), name='dermatologist'),
    path('dermatologist/<int:pk>/', DermatologistDetailView.as_view(), name='dermatologist-detail'),
    path('search/', views.ClinicSearch, name='clinic-search'),
    path('<int:pk>/delete', ClinicDeleteView.as_view(), name='clinic-delete'),
    path('<int:pk>/', ClinicDetailView.as_view(), name='clinic-detail'),
    path('new/', ClinicCreateView.as_view(), name='clinic-create'),
    path('<int:clinic_id>/booking/', ClinicBookingView.as_view(), name='clinic-booking'),
    path('<int:clinic_id>/booking/success/', BookingSuccessView.as_view(), name='booking-success'),  # New URL for success page
    path('<int:pk>/update', ClinicUpdateView.as_view(), name='clinic-update'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)