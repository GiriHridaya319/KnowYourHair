from django.shortcuts import render


def home(request):
    return render(request, 'base/homePage.html')


def hair_fall_prediction(request):
    return render(request, 'base/HairFallRiskPrediction.html', {'title': 'Prediction'})


def blog(request):
    return render(request, 'base/HairFallRiskPrediction.html', {'title': 'Prediction'})


def login(request):
    return render(request, 'base/HairFallRiskPrediction.html', {'title': 'Prediction'})


def registration(request):
    return render(request, 'base/HairFallRiskPrediction.html', {'title': 'Prediction'})
