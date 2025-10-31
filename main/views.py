from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from spare_parts.models import CarMake


class IndexListView(ListView):  # Или ваш существующий класс
    model = CarMake
    template_name = 'main/index.html'
    context_object_name = 'car_makes'

    def get_queryset(self):
        return CarMake.objects.all().order_by('name')

def about(request):
    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/contacts.html')