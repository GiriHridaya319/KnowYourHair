from django.urls import path
from . import views as user_view  # Make sure the views are correctly imported

urlpatterns = [
    path('', user_view.welcome, name='KnowYourHair-hairfallprediction'),
    path('survey/', user_view.survey, name='survey'),
    path('result/', user_view.predict_risk, name='result'),

]
