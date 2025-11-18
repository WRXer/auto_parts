"""The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from spare_parts.apps import SparePartsConfig
from spare_parts.views import PartListView, PartDetailView, CategoryDetailView, CarModelsAjaxView, \
    CarGenerationAjaxView, \
    CarModelListView, CarGenerationListView, PartsByGenerationView, DonorDetailView, part_detail_modal

app_name = SparePartsConfig.name


urlpatterns = [

    path('catalog/all_parts/', PartListView.as_view(), name='all_parts'),
    path('catalog/category/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('part/detail/modal/<int:part_pk>/', part_detail_modal, name='part_detail_modal'),
    path('catalog/part/<int:pk>/', PartDetailView.as_view(), name='part_detail'),
    path('cars/<int:make_pk>/models/', CarModelListView.as_view(), name='models_list'),
    path('cars/<int:make_pk>/models/<int:model_pk>/generations/', CarGenerationListView.as_view(), name='generations_list'),
    path('cars/<int:make_pk>/models/<int:model_pk>/generations/<int:generation_pk>/parts', PartsByGenerationView.as_view(), name='parts_by_generation'),
    path('donor/<int:pk>/', DonorDetailView.as_view(), name='donor_detail'),
    path('ajax/load-models/', CarModelsAjaxView.as_view(), name='ajax_load_car_models'),
    path('ajax/load-generations/', CarGenerationAjaxView.as_view(), name='ajax_load_car_generations'),
    path('search-by-number/', PartListView.as_view(), name='search_by_number'),
]
