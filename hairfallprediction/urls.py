from django.urls import path
from django.conf.urls.static import static
from KnowYourHair import settings
from . import views as user_view  # Make sure the views are correctly imported
from .views import RecomProductDetailView, SurveyView

urlpatterns = [
    path('', user_view.welcome, name='KnowYourHair-hairfallprediction'),
    path('survey/', SurveyView.as_view(), name='survey'),
    path('result/', user_view.predict_risk, name='result'),
    path('<slug:slug>/', RecomProductDetailView.as_view(), name='recom-product-detail'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
