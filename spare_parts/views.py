from django.views.generic import ListView
from rest_framework import generics
from spare_parts.models import Part
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