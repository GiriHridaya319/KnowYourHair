from django.urls import path
from . import views as user_view
from .views import AdminDashboardView, UserBookingView, UserDeleteView

urlpatterns = [
    path('profile/', user_view.profile, name='profile'),
    path('MyDetails/', user_view.agent_dashboard, name='agentDetails'),
    path('Details/', UserBookingView.as_view(), name='CustomerDetails'),
    path('profile/delete/<int:pk>/', UserDeleteView.as_view(), name='profile-delete'),
    path('profile/edit/', user_view.profile_update, name='profile-update'),
    path('profile/changePassword/', user_view.password, name='change-password'),
    path('login/', user_view.login_view, name='login'),
    path('adminBoard/', AdminDashboardView.as_view(), name='adminDash'),
    path('registration/', user_view.register, name='registration'),
    path('logout/', user_view.custom_logout, name='logout'),

    # New booking approval/rejection URLs
    path('booking/<int:pk>/approve/', user_view.approve_booking, name='approve_booking'),
    path('booking/<int:pk>/reject/', user_view.reject_booking, name='reject_booking'),

    path('clinic/<int:pk>/approve/', user_view.approve_clinic, name='approve_clinic'),
    path('clinic/<int:pk>/reject/', user_view.reject_clinic, name='reject_clinic'),

    path('product/<int:pk>/approve/', user_view.approve_product, name='approve_product'),
    path('product/<int:pk>/reject/', user_view.reject_product, name='reject_product'),
]