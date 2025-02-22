from django.urls import path
from . import views

# home is the function created in views
urlpatterns = [
    path('', views.home, name='KnowYourHair-home'),
    path('AboutUs/', views.About, name='KnowYourHair-AboutUs'),
    path('Blog/', views.blog, name='KnowYourHair-blog'),
]
