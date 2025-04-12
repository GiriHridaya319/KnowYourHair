from django.urls import path
from django.conf.urls.static import static
from KnowYourHair import settings
from . import views as user_view, views  # Make sure the views are correctly imported
from .views import RecomProductDetailView, SurveyView

urlpatterns = [
    path('', user_view.welcome, name='KnowYourHair-hairfallprediction'),
    path('survey/', user_view.SurveyView, name='survey'),
    path('result/', user_view.predict_risk, name='result'),
    path('export-survey-pdf/', views.export_survey_pdf, name='export_survey_pdf'),
    path('<slug:slug>/', RecomProductDetailView.as_view(), name='recom-product-detail'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
