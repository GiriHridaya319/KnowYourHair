from django.urls import path
from . import views

# home is the function created in views
urlpatterns = [
    path('', views.home, name='hair-home'),
    path('hairfallprediction/', views.hair_fall_prediction, name='hair-hairfallprediction'),
    path('Blog/', views.blog, name='hair-blog'),
    path('login/', views.login, name='hair-login'),
    path('registration/', views.registration, name='hair-registration'),
]