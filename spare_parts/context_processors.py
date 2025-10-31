from .models import Category


def categories(request):
    """
    Добавляет список всех активных категорий в контекст всех шаблонов.
    """
    return {
        'categories': Category.objects.all().order_by('name')
    }