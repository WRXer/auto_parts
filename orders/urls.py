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
from orders import views


app_name = 'orders'


urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('update_status/<int:order_id>/', views.update_order_status, name='update_status'),
    path('update_paid_status/<int:order_id>/', views.update_paid_status, name='update_paid_status'),
]