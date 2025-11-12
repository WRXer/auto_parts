from .models import Category


def all_categories(request):
    """
    Добавляет список всех активных категорий в контекст всех шаблонов.
    """
    return {
        'all_categories': Category.objects.all().order_by('name')
    }