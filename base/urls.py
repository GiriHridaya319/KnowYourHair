from django.urls import path
from . import views
from .views import Home

# home is the function created in views
urlpatterns = [
    path('', Home.as_view(), name='KnowYourHair-home'),
    path('AboutUs/', views.About, name='KnowYourHair-AboutUs'),
    path('Blog/', views.blog, name='KnowYourHair-blog'),
    path('faq/', views.helpSupport, name='KnowYourHair-HelpAndSupport'),
]
