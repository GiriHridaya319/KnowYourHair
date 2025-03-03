from django.shortcuts import render
from hairfallprediction.models import Product
from django.views.generic import ListView, DetailView, CreateView


def hair_fall_prediction(request):
    return render(request, 'base/HairFallRiskPrediction.html', {'title': 'Prediction'})


def blog(request):
    return render(request, 'base/Blog.html', {'title': 'Blog'})


def helpSupport(request):
    return render(request, 'base/helpandsupport.html', {'title': 'FAQ&Help'})


def About(request):
    return render(request, 'base/AboutUs.html', {'title': 'About Us'})


class Home(ListView):
    model = Product
    template_name = 'base/home.html'
    context_object_name = 'products'
