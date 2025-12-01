from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from spare_parts.models import CarMake, DonorVehicle


class IndexListView(ListView):  # Или ваш существующий класс
    model = CarMake
    template_name = 'main/index.html'
    context_object_name = 'car_makes'

    def get_queryset(self):
        return CarMake.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_arrivals'] = DonorVehicle.objects.select_related('generation__model__make').prefetch_related('images').order_by('-arrival_date')[:4]
        return context

def about(request):
    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/contacts.html')

def delivery(request):
    return render(request, 'main/delivery.html')