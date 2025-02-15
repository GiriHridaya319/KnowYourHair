from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .ml_models.predictor import HairfallPredictor
from .ml_models.recommender import ProductRecommender
from .models import Product
from django.contrib import messages


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

    # If GET request, show the product selection form
    return render(request, 'hairfallprediction/recom_product_detail.html')


class RecomProductDetailView(DetailView):
    model = Product
    template_name = 'hairfallprediction/recom_product_detail.html'
    context_object_name = 'product'  # This will be the name of the object in the template

    def get_object(self):
        # Retrieve the product based on the name passed in the URL
        return get_object_or_404(Product, name=self.kwargs['name'])

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        # Get the product object
        product = self.get_object()

        # Get the hybrid recommendations for the product
        recommendations = recommender.get_hybrid_recommendations(product.name)
        print("Recommendations structure:", recommendations)

        if hasattr(recommendations, 'to_dict'):
            recommendations = recommendations.to_dict('records')
        formatted_recommendations = []
        for rec in recommendations:
            formatted_rec = {
                'name': rec.get('name', ''),
                'image': rec.get('image', ''),
                'details': rec.get('details', ''),
                'cost': rec.get('cost', ''),
                'HybridScore': rec.get('HybridScore', 0)
            }
            formatted_recommendations.append(formatted_rec)

        context['recommendations'] = formatted_recommendations
        context['selected_product'] = product.name

        return context
