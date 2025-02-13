from django.shortcuts import render,redirect
from django.http import JsonResponse
from .ml_models.predictor import HairfallPredictor
from .ml_models.recommender import ProductRecommender


def welcome(request):
    return render(request, 'hairfallprediction/welcomePage.html')


def survey(request):
    return render(request, 'hairfallprediction/survey.html', {'title': 'survey'})




# Initialize the predictor and recommender

predictor = HairfallPredictor()
recommender = ProductRecommender()


def predict_risk(request):
    """Handle the prediction form submission and display results."""
    if request.method == 'POST':
        # Extract user data from the form
        user_data = {
            'Gender': int(request.POST.get('Gender')),
            'Age': int(request.POST.get('Age')),
            'Hairline Pattern': int(request.POST.get('Hairline_Pattern')),
            'Hair Fall Rate': int(request.POST.get('Hair_Fall_Rate')),
            'Nutrition': int(request.POST.get('Nutrition')),
            'Chemical Product Usage': int(request.POST.get('Chemical_Product_Usage')),
            'Genetics': int(request.POST.get('Genetics')),
            'Past Chronic Illness': int(request.POST.get('Past_Chronic_Illness')),
            'Sleep Disturbance': int(request.POST.get('Sleep_Disturbance')),
            'Water Quality Issue': int(request.POST.get('Water_Quality_Issue')),
            'Stress': int(request.POST.get('Stress')),
            'Food Habit': int(request.POST.get('Food_Habit')),
            'Hormonal Changes': int(request.POST.get('Hormonal_Change')),
            'Hair Care Habits': int(request.POST.get('Hair_Care_Habits')),
            'Smoking': int(request.POST.get('Smoking')),
        }

        # age and risk level comes from here
        prediction_result = predictor.predict_risk(user_data)

        # Get product recommendations based on risk level
        recommendations, _ = recommender.get_recommendations_risk(prediction_result['risk_level'])

        # Prepare context for the template
        context = {
            'prediction_result': prediction_result['risk_level'],
            'age_prediction': prediction_result['age_prediction'],
            'recommendations': recommendations,
        }

        return render(request, 'hairfallprediction/resultPage.html', context)

    return redirect('survey')
