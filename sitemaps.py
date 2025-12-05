from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from spare_parts.models import Part, Category


class StaticSitemap(Sitemap):
    """
    Карта сайта для статических страниц (О нас, Контакты и т.д.)
    """
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['index', 'contacts', 'about', 'delivery', 'payment']    #Имена URL-маршрутов ваших статических страниц

    def location(self, item):
        return reverse(item)    #Используем reverse для получения абсолютного пути


class PartSitemap(Sitemap):
    """
    Карта сайта для всех страниц товаров
    """
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return Part.objects.all()

    def location(self, obj):
        return reverse('spare_parts:part_detail', args={obj.pk})

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None


class CategorySitemap(Sitemap):
    """
    Карта сайта для страниц категорий
    """
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('spare_parts:category_detail', kwargs={'category_slug': obj.slug})