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
from main import views
from spare_parts.apps import SparePartsConfig
from spare_parts.views import PartListAPIView, PartRetieveAPIView

app_name = SparePartsConfig.name


urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/all_parts/', PartListAPIView.as_view(), name='all_parts'),
    path('catalog/part/<int:pk>/', PartRetieveAPIView.as_view(), name='part_get'),
]
