from django.urls import path
from . import views as user_view  # Make sure the views are correctly imported

urlpatterns = [
    path('profile/', user_view.profile, name='profile'),  # Profile view
    path('profile/edit/', user_view.profile_update, name='profile-update'),
    path('profile/changePassword/', user_view.password, name='change-password'),# Profile update
    path('login/', user_view.login_view, name='login'),  # Login view
    path('registration/', user_view.register, name='registration'),  # Registration view
    path('logout/', user_view.custom_logout, name='logout'),  # Logout view
]
