import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from KnowYourHair import settings
from .ml_models.predictor import HairfallPredictor
from .ml_models.recommender import ProductRecommender
from .models import Product
from django.contrib import messages

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.views.decorators.http import require_POST
import io
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import textwrap


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

        # Get prediction
        prediction_result = predictor.predict_risk(user_data)

        # Get recommendations
        recommendations, _ = recommender.get_recommendations_risk(prediction_result['risk_level'])

        for rec in recommendations:
            # Check if the file exists in the media directory
            if rec['image']:
                full_path = os.path.join(settings.MEDIA_ROOT, str(rec['image']))

        # Process recommendations to ensure proper image URLs
        for rec in recommendations:
            if rec['image']:
                # If the image path doesn't start with MEDIA_URL, add it
                if not str(rec['image']).startswith('/media/'):
                    rec['image'] = os.path.join(settings.MEDIA_URL, str(rec['image']))

        # Prepare context with additional debug info
        context = {
            'prediction_result': prediction_result['risk_level'],
            'age_prediction': prediction_result['age_prediction'],
            'recommendations': recommendations,
            'MEDIA_URL': settings.MEDIA_URL,
            'DEBUG': settings.DEBUG,
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

            # Process recommendations to ensure proper image URLs
            for rec in recommendations:
                if rec['image']:
                    # Check if the file exists in the media directory
                    full_path = os.path.join(settings.MEDIA_ROOT, str(rec['image']))

                    # If the image path doesn't start with MEDIA_URL, add it
                    if not str(rec['image']).startswith('/media/'):
                        rec['image'] = os.path.join(settings.MEDIA_URL, str(rec['image']))

            context = {
                'selected_product': product_name,
                'recommendations': recommendations,
                'MEDIA_URL': settings.MEDIA_URL,
                'DEBUG': settings.DEBUG,
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


# survey form save

@require_POST
def export_survey_pdf(request):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF object using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    # Create a list to store our elements
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    subheading_style = styles['Heading3']
    normal_style = styles['Normal']

    # Add custom styles
    risk_style = ParagraphStyle(
        'RiskStyle',
        parent=styles['Heading2'],
        textColor=colors.red if request.POST.get('prediction_result') == 'High Risk' else
        colors.orange if request.POST.get('prediction_result') == 'Medium Risk' else
        colors.green
    )

    # Add title
    elements.append(Paragraph("Hair Health Analysis Report", title_style))
    elements.append(Spacer(1, 20))

    # Add risk assessment section
    elements.append(Paragraph("Risk Assessment", heading_style))
    elements.append(Spacer(1, 10))

    # Get prediction result and age prediction from POST data
    prediction_result = request.POST.get('prediction_result')
    if not prediction_result:
        # If not directly provided, we can add fallback logic here
        # This assumes you're storing it in session or recalculating
        prediction_result = "Not Available"

    elements.append(Paragraph(f"Hair Fall Risk Level: {prediction_result}", risk_style))
    elements.append(Spacer(1, 10))

    # Add age prediction if not low risk
    if prediction_result != 'Low Risk':
        age_prediction_years = request.POST.get('age_prediction_years')
        if age_prediction_years:
            elements.append(Paragraph(f"Predicted Hair Loss Onset: Age {age_prediction_years}", normal_style))
            elements.append(Spacer(1, 10))
    else:
        elements.append(Paragraph(
            "Based on your current hair health patterns, you are at a low risk for hair loss and in a safe zone.",
            normal_style))

    elements.append(Spacer(1, 15))

    # Add prevention tips section
    elements.append(Paragraph("Prevention Tips", heading_style))
    elements.append(Spacer(1, 10))

    # Add different tips based on risk level
    if prediction_result == 'High Risk':
        tips = [
            ("Consult Specialist", "Schedule an appointment with a trichologist"),
            ("Medical Treatment", "Consider prescribed medications and treatments"),
            ("Balanced Diet", "Include biotin, iron, and protein-rich foods daily"),
            ("Avoid Chemicals", "Strictly avoid chemical treatments and harsh styling"),
            ("Stress Management", "Implement daily stress-reduction techniques")
        ]
    elif prediction_result == 'Medium Risk':
        tips = [
            ("Balanced Diet", "Focus on hair-healthy nutrients and vitamins"),
            ("Avoid Chemicals", "Minimize use of chemical treatments and heat styling"),
            ("Stress Management", "Regular exercise and relaxation practices")
        ]
    else:  # Low Risk
        tips = [
            ("Balanced Diet", "Maintain a healthy diet with balanced nutrients"),
            ("Avoid Chemicals", "Use natural products and gentle styling methods"),
            ("Stress Management", "Maintain a balanced lifestyle and good sleep habits")
        ]

    for tip_title, tip_desc in tips:
        elements.append(Paragraph(tip_title, subheading_style))
        elements.append(Paragraph(tip_desc, normal_style))
        elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 15))

    # Add survey results section
    elements.append(Paragraph("Survey Inputs", heading_style))
    elements.append(Spacer(1, 15))

    # Extract all form data
    form_data = {
        'Gender': request.POST.get('Gender'),
        'Age': request.POST.get('Age'),
        'Hairline Pattern': request.POST.get('Hairline_Pattern'),
        'Hair Fall Rate': request.POST.get('Hair_Fall_Rate'),
        'Nutrition': request.POST.get('Nutrition'),
        'Chemical Product Usage': request.POST.get('Chemical_Product_Usage'),
        'Genetics': request.POST.get('Genetics'),
        'Past Chronic Illness': request.POST.get('Past_Chronic_Illness'),
        'Sleep Disturbance': request.POST.get('Sleep_Disturbance'),
        'Water Quality Issue': request.POST.get('Water_Quality_Issue'),
        'Stress': request.POST.get('Stress'),
        'Food Habit': request.POST.get('Food_Habit'),
        'Hormonal Changes': request.POST.get('Hormonal_Change'),
        'Hair Care Habits': request.POST.get('Hair_Care_Habits'),
        'Smoking': request.POST.get('Smoking'),
    }

    # Define human-readable labels and values for each field
    field_labels = {
        'Gender': {
            'question': 'Gender',
            'options': {
                '0': 'Female',
                '1': 'Male',
                '2': 'Other'
            }
        },
        'Age': {
            'question': 'Age',
            'value': lambda x: f"{x} years"
        },
        'Hairline Pattern': {
            'question': 'Hairline Pattern',
            'options': {
                '0': 'Normal',
                '1': 'Pattern 1',
                '2': 'Pattern 2',
                '3': 'Pattern 3',
                '4': 'Pattern 4',
                '5': 'Pattern 5'
            }
        },
        'Hair Fall Rate': {
            'question': 'Hair Fall Rate',
            'options': {
                '35': '20-50 strands/day',
                '65': '50-80 strands/day',
                '95': '80-110 strands/day',
                '125': '110-140 strands/day',
                '155': '140-170 strands/day',
                '185': '170-200 strands/day',
                '215': '200-230 strands/day'
            }
        },
        'Nutrition': {
            'question': 'Nutrition Level',
            'value': lambda x: f"{x}/10 - {'Poor' if int(x) <= 3 else 'Average' if int(x) <= 7 else 'Excellent'}"
        },
        'Chemical Product Usage': {
            'question': 'Chemical Product Usage',
            'options': {
                '0': 'Never - I avoid chemical products',
                '1': 'Occasionally - A few times a year',
                '2': 'Regularly - Monthly use',
                '3': 'Frequently - Weekly use'
            }
        },
        'Genetics': {
            'question': 'Family History',
            'options': {
                '0': 'No family history of hair loss',
                '1': 'Some relatives have hair loss',
                '2': 'Strong family history of hair loss'
            }
        },
        'Past Chronic Illness': {
            'question': 'Medical History',
            'options': {
                '0': 'No chronic illness history',
                '1': 'Yes, mild conditions',
                '2': 'Yes, severe conditions'
            }
        },
        'Sleep Disturbance': {
            'question': 'Sleep Patterns',
            'options': {
                '0': 'Excellent (7-9 hours nightly)',
                '1': 'Good (6-7 hours)',
                '2': 'Fair (5-6 hours)',
                '3': 'Sleep disorder/Insomnia'
            }
        },
        'Water Quality Issue': {
            'question': 'Water Quality',
            'options': {
                '0': 'Excellent - Soft or filtered water',
                '1': 'Moderate - Some mineral content',
                '2': 'Poor - Hard water with high mineral content'
            }
        },
        'Stress': {
            'question': 'Stress Levels',
            'options': {
                '0': 'Minimal - Well managed stress',
                '1': 'Moderate - Occasional stress',
                '2': 'High - Frequent stress',
                '3': 'Severe - Constant stress'
            }
        },
        'Food Habit': {
            'question': 'Dietary Habits',
            'options': {
                '0': 'Balanced - Regular nutritious meals',
                '1': 'Moderate - Occasionally skip meals',
                '2': 'Poor - Frequent fast food',
                '3': 'Very Poor - Irregular eating patterns'
            }
        },
        'Hormonal Changes': {
            'question': 'Hormonal Changes',
            'options': {
                '0': 'Balanced - No noticeable changes',
                '1': 'Unbalanced - Noticeable changes or symptoms'
            }
        },
        'Hair Care Habits': {
            'question': 'Hair Care Routine',
            'options': {
                '0': 'Excellent - Professional care with regular maintenance',
                '1': 'Very Good - Regular care with quality products',
                '2': 'Good - Basic regular care routine',
                '3': 'Moderate - Inconsistent care routine',
                '4': 'Poor - Minimal hair care',
                '5': 'Inadequate - Neglected hair care'
            }
        },
        'Smoking': {
            'question': 'Smoking Habits',
            'options': {
                '0': 'No - Never smoked',
                '1': 'Yes - Regular smoker'
            }
        }
    }

    # Process each field
    for field_name, value in form_data.items():
        if value:
            field_info = field_labels.get(field_name, {'question': field_name})

            # Add section heading
            elements.append(Paragraph(field_info['question'], subheading_style))
            elements.append(Spacer(1, 5))

            # Add answer value
            if 'options' in field_info and value in field_info['options']:
                answer_text = field_info['options'][value]
            elif 'value' in field_info:
                answer_text = field_info['value'](value)
            else:
                answer_text = value

            elements.append(Paragraph(f"Selected: {answer_text}", normal_style))
            elements.append(Spacer(1, 10))

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf_value = buffer.getvalue()
    buffer.close()

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(pdf_value, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Hair_Analysis_Report.pdf"'

    return response