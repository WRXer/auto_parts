from .models import PartSubCategory, Category


def all_categories(request):
    """
    Добавляет список всех активных категорий в контекст всех шаблонов.
    """
    return {
        'all_categories': Category.objects.all().order_by('name')
    }

def categories_processor(request):
    """
    Предоставляет список основных категорий для отображения в шаблонах.
    """
    # 🔑 Получаем choices через поле модели (мета-API Django)
    # Это работает независимо от того, где определен список.
    return {
        'all_categories': PartSubCategory.objects.all().order_by('title')
    }