from django.views.generic import ListView, DetailView
from rest_framework import generics
from spare_parts.models import Part, Category
from spare_parts.serializers import PartSerializer


class PartRetieveAPIView(generics.RetrieveAPIView):
    """
    Вывод одной запчасти
    """
    serializer_class = PartSerializer
    queryset = Part.objects.all()


class PartListView(ListView):
    """
    Это представление будет рендерить HTML-страницу со списком запчастей.
    """
    model = Part
    template_name = 'main/all_parts.html'
    context_object_name = 'all_parts'    #Имя, по которому вы обращаться к списку в HTML

    def get_queryset(self):
        return Part.objects.all().order_by('-created_at')    #Опционально: фильтруем запчасти

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    #Опционально: добавляем категории в контекст для меню
        return context


class PartDetailView(DetailView):
    """
    Вывод одной запчасти в веб
    """
    model = Part
    template_name = 'main/part_detail.html'
    context_object_name = 'part'


class CategoryListView(ListView):
    """
    Выводит список запчастей, отфильтрованных по выбранной категории (category_id).
    """
    model = Part
    template_name = 'main/category_detail.html'
    context_object_name = 'parts'
    paginate_by = 10     #Пагинация

    def get_queryset(self):
        category_id = self.kwargs['category_id']     #Получаем ID категории из URL-адреса
        queryset = Part.objects.filter(category_id=category_id)            #Фильтруем запчасти: возвращаем только те, которые относятся к этой категории
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     #Добавляем объект категории в контекст для использования в заголовке шаблона
        category_id = self.kwargs['category_id']
        context['category'] = Category.objects.get(id=category_id)    #Получаем объект Category
        return context