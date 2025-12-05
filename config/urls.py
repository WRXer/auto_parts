"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from sitemaps import StaticSitemap, PartSitemap, CategorySitemap


sitemaps = {
    'static': StaticSitemap,
    'parts': PartSitemap,
    'categories': CategorySitemap,
}


urlpatterns = [
    path(settings.SECRET_ADMIN_PATH, admin.site.urls),
    path('', include('main.urls')),
    path('', include('spare_parts.urls', namespace='spare_parts')),
    path('', include('users.urls')),
    path('carts/', include('carts.urls')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)