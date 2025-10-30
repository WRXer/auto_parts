from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'main/index.html')

def about(request):
    return HttpResponse("About site")

def contacts(request):
    return render(request, 'main/contacts.html')