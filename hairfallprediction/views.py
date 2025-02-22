from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .ml_models.predictor import HairfallPredictor
from .ml_models.recommender import ProductRecommender
from .models import Product
from django.contrib import messages


def welcome(request):
    return render(request, 'hairfallprediction/welcomePage.html')


@login_required
def SurveyView(request):
    return render(request, 'hairfallprediction/survey.html')


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


def recommendation_hybrid(request):
    """Display hybrid recommendations for a selected product."""
    if request.method == 'POST':
        try:
            # Get the selected product name
            product_name = request.POST.get('name')
            if not product_name:
                messages.error(request, 'Please select a product')
                return render(request, 'hairfallprediction/recom_product_detail.html')

            # Get recommendations based on the selected product
            recommendations = recommender.get_hybrid_recommendations(product_name)

            context = {
                'selected_product': product_name,
                'recommendations': recommendations,
            }

            return render(request, 'hairfallprediction/recom_product_detail.html', context)

        except Exception as e:
            messages.error(request, 'Error generating recommendations')
            return render(request, 'hairfallprediction/recom_product_detail.html')

    def get_object(self):
        return get_object_or_404(Product, name=self.kwargs['slug'])

    # If GET request, show the product selection form
    return render(request, 'hairfallprediction/recom_product_detail.html')


class RecomProductDetailView(DetailView):
    model = Product
    template_name = 'hairfallprediction/recom_product_detail.html'
    context_object_name = 'product'

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        try:
            # Get the product object
            product = self.get_object()

            # Get the hybrid recommendations for the product
            recommendations = recommender.get_hybrid_recommendations(product.name)
            context['recommendations'] = recommendations
            context['selected_product'] = product.name

        except Exception as e:
            print(f"Error in get_context_data: {str(e)}")
            context['recommendations'] = []
            context['error_message'] = str(e)

        return context
