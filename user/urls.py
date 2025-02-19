from django.urls import path
from . import views as user_view
from .views import AdminDashboardView

urlpatterns = [
    path('profile/', user_view.profile, name='profile'),
    path('profile/edit/', user_view.profile_update, name='profile-update'),
    path('profile/changePassword/', user_view.password, name='change-password'),
    path('login/', user_view.login_view, name='login'),
    path('adminBoard/', AdminDashboardView.as_view(), name='adminDash'),
    path('registration/', user_view.register, name='registration'),
    path('logout/', user_view.custom_logout, name='logout'),
]
