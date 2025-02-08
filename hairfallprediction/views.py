from django.shortcuts import render


def welcome(request):
    return render(request, 'hairfallprediction/welcomePage.html')


def survey(request):
    return render(request, 'hairfallprediction/survey.html', {'title': 'survey'})


def result(request):
    return render(request, 'base/resultPage.html', {'title': 'Result'})


# Create your views here.
