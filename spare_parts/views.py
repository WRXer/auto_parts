from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import resolve
from django.views import View
from django.views.generic import ListView, DetailView
from rest_framework import generics
from spare_parts.models import Part, Category, CarModel, CarMake, CarGeneration
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
    context_object_name = 'all_parts'    #Имя, по которому вы обращаться к списку в HTML
    paginate_by = 10

    def get_template_names(self):
        """
        К разному урлу своя страница
        :return:
        """
        resolved_url = resolve(self.request.path_info)   #Получаем информацию о текущем URL-адресе, который вызвал эту вьюху
        if resolved_url.url_name == 'search_by_number':
            return ['main/search_results.html']
        else:
            return ['main/all_parts.html']    #Для остальных случаев (каталог, фильтры по авто) используем основной шаблон

    def get_queryset(self):
        queryset = super().get_queryset().select_related('donor_generation')    #Получаем базовый QuerySet
        selected_make = self.request.GET.get('make')
        selected_model = self.request.GET.get('model')
        selected_generation = self.request.GET.get('generation')    #ID CarGeneration
        filters = {}
        if selected_generation:
            filters['donor_generation_id'] = selected_generation
        elif selected_model:
            filters['donor_generation__model__id'] = selected_model
        elif selected_make:
            filters['donor_generation__model__make__id'] = selected_make
        if filters:
            queryset = queryset.filter(**filters)

        part_number_query = self.request.GET.get('part_number')
        if part_number_query:
            normalized_query = part_number_query.strip().replace(' ', '').replace('-', '').upper()    #Нормализуем запрос: убираем пробелы и тире, переводим в верхний регистр
            queryset = queryset.filter(Q(part_number__iexact=normalized_query) | Q(part_number__icontains=normalized_query)).distinct()    #Используем Q для поиска по точному совпадению И частичному совпадению
            self.extra_context = {'search_query': part_number_query}    #Добавляем запрос в контекст, чтобы показать его в заголовке шаблона
        return queryset.order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car_makes'] = CarMake.objects.all().order_by('name')    #Загружаем все марки для формы поиска
        selected_make_id = self.request.GET.get('make')
        selected_model_id = self.request.GET.get('model')
        selected_generation_id = self.request.GET.get('generation')
        header_context = {}
        if selected_make_id:
            try:
                make = CarMake.objects.get(pk=selected_make_id)
                header_context['make'] = make.name
            except CarMake.DoesNotExist:
                pass
        if selected_model_id and not selected_generation_id:
            try:
                model = CarModel.objects.get(pk=selected_model_id)
                header_context['model'] = model.name
            except CarModel.DoesNotExist:
                pass
        if selected_generation_id:
            try:
                generation = CarGeneration.objects.get(pk=selected_generation_id)
                header_context['generation'] = generation.name
                header_context['model'] = generation.model.name
                header_context['make'] = generation.model.make.name
            except CarGeneration.DoesNotExist:
                pass
        context['header_info'] = header_context
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

class CarModelListView(ListView):
    """
    Отображает список моделей для конкретной марки.
    """
    model = CarModel
    template_name = 'main/models_list.html'
    context_object_name = 'car_models'

    def get_queryset(self):
        make_pk = self.kwargs.get('make_pk')    #Получаем ID марки из URL (из path, не из GET)
        try:
            self.make = CarMake.objects.get(pk=make_pk)
        except CarMake.DoesNotExist:
             self.make = get_object_or_404(CarMake, pk=make_pk)

        return CarModel.objects.filter(make=self.make).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        make_pk = self.kwargs.get('make_pk')
        try:
            context['current_make'] = CarMake.objects.get(pk=make_pk)    #Получаем объект Марки для заголовка
        except CarMake.DoesNotExist:
            context['current_make'] = None
        return context


class CarGenerationListView(ListView):
    """
    Отображает список поколений для конкретной модели.
    """
    model = CarGeneration
    template_name = 'main/generations_list.html'
    context_object_name = 'generations_list'

    def get_queryset(self):
        make_pk = self.kwargs.get('make_pk')
        model_pk = self.kwargs.get('model_pk')
        self.model_obj = get_object_or_404(CarModel.objects.select_related('make'),pk=model_pk,make__pk=make_pk)
        return CarGeneration.objects.filter(model=self.model_obj).order_by('-year_start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_model'] = self.model_obj
        context['current_make'] = self.model_obj.make
        return context


class CarModelsAjaxView(View):
    """
    Класс-ориентированный View для обработки AJAX-запроса:
    возвращает список моделей в формате JSON, отфильтрованных по make_id.
    """
    def get(self, request, *args, **kwargs):
        make_id = request.GET.get('make_id')    #Получаем make_id из GET-запроса (например, make_id=5)
        if not make_id:
            return JsonResponse([], safe=False)
        try:
            models = CarModel.objects.filter(make_id=make_id).order_by('name')    #Фильтруем модели по make_id
        except Exception:
            return JsonResponse([], safe=False)  # Обработка возможных ошибок, например, неверный ID
        model_list = []  #Формируем список словарей для JSON-ответа
        for model in models:
            model_list.append({'id': model.id, 'name': model.name})
        return JsonResponse(model_list, safe=False)    #Возвращаем JSON-ответ


class CarGenerationAjaxView(View):
    """
    CBV для AJAX: возвращает список модификаций, отфильтрованных по model_id.
    """
    def get(self, request, *args, **kwargs):
        model_id = request.GET.get('model_id')   #Получаем ID модели из GET-запроса
        if not model_id:
            return JsonResponse([], safe=False)
        generations = CarGeneration.objects.filter(model_id=model_id).values('id', 'name').order_by('name')    #Выполняем запрос к базе
        return JsonResponse(list(generations), safe=False)    #Возвращаем JSON-ответ


class PartsByGenerationView(ListView):
    """
    Отображает список запчастей, отфильтрованных по выбранной Генерации (модификации).
    """
    model = Part
    template_name = 'main/parts_by_generation.html'
    context_object_name = 'parts_list'
    paginate_by = 10

    def get_queryset(self):
        generation_pk = self.kwargs.get('generation_pk')
        self.generation_obj = get_object_or_404(CarGeneration, pk=generation_pk)
        return Part.objects.filter(donor_generation=self.generation_obj).order_by('title')    #Фильтруем запчасти, связанные с этой Генерацией

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_generation'] = self.generation_obj
        return context