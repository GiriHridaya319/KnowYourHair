from django.urls import path
from . import views as user_view
from .views import AdminDashboardView, UserBookingView, UserDeleteView
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [
    path('profile/', user_view.profile, name='profile'),
    path('MyDetails/', user_view.agent_dashboard, name='agentDetails'),
    path('Details/', UserBookingView.as_view(), name='CustomerDetails'),
    path('profile/delete/<int:pk>/', UserDeleteView.as_view(), name='profile-delete'),
    path('profile/edit/', user_view.profile_update, name='profile-update'),

    # Password reset paths
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='user/password_reset.html',
             form_class=CustomPasswordResetForm,
             email_template_name='user/password_reset_email.html',
             html_email_template_name='user/password_reset_html_email.html',
             subject_template_name='user/password_reset_subject.txt',
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='user/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='user/changePassword.html',
             form_class=CustomSetPasswordForm,
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='user/passwordResetComplete.html'
         ),
         name='password_reset_complete'),

    # Authentication paths
    path('login/', user_view.login_view, name='login'),
    path('adminBoard/', AdminDashboardView.as_view(), name='adminDash'),
    path('registration/', user_view.register, name='registration'),
    path('logout/', user_view.custom_logout, name='logout'),

    # New agent approval paths
    path('pending-approval/', user_view.pending_approval, name='pending_approval'),
    path('user/agent-approvals/', user_view.agent_approval_list, name='agent_approval_list'),
    path('user/agent/<int:pk>/approve/', user_view.approve_agent, name='approve_agent'),
    path('user/agent/<int:pk>/reject/', user_view.reject_agent, name='reject_agent'),

    # Existing approval/rejection URLs
    path('booking/<int:pk>/approve/', user_view.approve_booking, name='approve_booking'),
    path('booking/<int:pk>/reject/', user_view.reject_booking, name='reject_booking'),
    path('clinic/<int:pk>/approve/', user_view.approve_clinic, name='approve_clinic'),
    path('clinic/<int:pk>/reject/', user_view.reject_clinic, name='reject_clinic'),
    path('product/<int:pk>/approve/', user_view.approve_product, name='approve_product'),
    path('product/<int:pk>/reject/', user_view.reject_product, name='reject_product'),
]