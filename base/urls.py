from django.urls import path
from . import views

# home is the function created in views
urlpatterns = [
    path('', views.home, name='KnowYourHair-home'),
    path('hairfallprediction/', views.hair_fall_prediction, name='KnowYourHair-hairfallprediction'),
    path('Blog/', views.blog, name='KnowYourHair-blog'),
    path('login/', views.login, name='KnowYourHair-login'),
    path('registration/', views.registration, name='KnowYourHair-registration'),
]
