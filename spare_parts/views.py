from django.db.models import Count, Q
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import resolve
from django.views import View
from django.views.generic import ListView, DetailView
from rest_framework import generics
from carts.cart import Cart
from carts.forms import CartAddPartForm
from spare_parts.models import Part, Category, CarModel, CarMake, CarGeneration, DonorVehicle
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
        queryset = super().get_queryset()    #Получаем базовый QuerySet
        queryset = queryset.filter(is_active=True)
        search_query = self.request.GET.get('part_number')  # Получаем текстовый запрос
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) |  Q(description__icontains=search_query) |  Q(part_number__icontains=search_query)  ).distinct()    #Ищем совпадения в нескольких полях, используя Q-объекты (логика ИЛИ)
        donor_vehicle_id = self.request.GET.get('donor_vehicle_id')
        if donor_vehicle_id and donor_vehicle_id.isdigit():   #Если клик был с карточки "Новое поступление"
            queryset = queryset.filter(donor_vehicle_id=donor_vehicle_id)
            return queryset.order_by('title').select_related('donor_vehicle', 'donor_generation__model__make', 'category').prefetch_related('images')

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
            queryset = queryset.select_related('donor_generation').filter(**filters).distinct()
        else:
            queryset = queryset.prefetch_related('donor_generation')
        category_id = self.request.GET.get('category')   #Фильтр по категории
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        queryset = queryset.select_related('donor_vehicle', 'donor_generation__model__make','category').prefetch_related('images')
        return queryset.order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('part_number', '')
        context['search_query'] = search_query
        context['part_number'] = search_query
        donor_vehicle_id = self.request.GET.get('donor_vehicle_id')
        if donor_vehicle_id and donor_vehicle_id.isdigit():
            try:
                donor = DonorVehicle.objects.select_related('generation__model__make').get(pk=donor_vehicle_id)
                context['header_info'] = {'make': donor.generation.model.make.name,'model': donor.generation.model.name,'generation': f"{donor.generation.name} (Поступление: {donor.title})"}
                context['car_makes'] = CarMake.objects.all().order_by('name')
                context['categories'] = Category.objects.all().order_by('name')
                return context
            except DonorVehicle.DoesNotExist:
                pass
        context['car_makes'] = CarMake.objects.all().order_by('name')    #Загружаем все марки для формы поиска
        context['categories'] = Category.objects.all().order_by('name')
        selected_make_id = self.request.GET.get('make')
        selected_model_id = self.request.GET.get('model')
        selected_generation_id = self.request.GET.get('generation')
        header_context = {}
        if selected_make_id:
            try:
                make = CarMake.objects.get(pk=selected_make_id)
                header_context['make'] = make.name
                context['car_models'] = CarModel.objects.filter(make=make).order_by('name')
            except CarMake.DoesNotExist:
                context['car_models'] = []
        else:
            context['car_models'] = []
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
        if selected_model_id:     #Предзаполнение модификаций для выбранной модели
            context['car_generations'] = CarGeneration.objects.filter(model_id=selected_model_id).order_by('name')
        else:
            context['car_generations'] = []
        query_params = self.request.GET.copy()    #GET-параметры без фильтра по авто для кнопки "Сбросить авто"
        query_params_without_auto = query_params.copy()
        for key in ['make', 'model', 'generation']:
            query_params_without_auto.pop(key, None)
        context['query_params_without_auto'] = query_params_without_auto
        return context


def part_detail_modal(request, pk):
    """
    Загружает HTML-фрагмент для модального окна.
    """
    part = get_object_or_404(Part, pk=pk)
    cart = Cart(request)    #Инициализируем корзину

    is_part_in_cart = str(part.id) in cart.cart    #Проверяем, есть ли запчасть в корзине
    cart_add_form = CartAddPartForm(initial={'quantity': 1, 'override': False})
    context = {
        'part': part,
        'cart_add_form': cart_add_form,
        'is_part_in_cart': is_part_in_cart,
    }
    html = render_to_string('main/part_detail_fragment.html', context, request=request)
    return HttpResponse(html, content_type="text/html; charset=utf-8")



class PartDetailView(DetailView):
    """
    Вывод одной запчасти в веб
    """
    model = Part
    template_name = 'main/part_detail.html'
    context_object_name = 'part'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 🔑 Добавляем форму корзины в контекст
        context['cart_add_form'] = CartAddPartForm()

        return context


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


class CategoryDetailView(ListView):
    """
    Отображает список запчастей для конкретной категории.
    Фильтр отображает полный список автомобилей, а QuerySet фильтрует запчасти по выбранной машине.
    """
    model = Part
    template_name = 'main/category_detail.html'
    context_object_name = 'parts'
    paginate_by = 10

    def get_category_id(self):
        """
        Находит ID категории, считывая его из именованного аргумента URL (pk),
        либо из GET-параметра (category).
        """
        # Читаем pk из именованных аргументов URL (из-за <int:pk>/ в urls.py)
        category_pk = self.kwargs.get('pk')

        # Если pk нет в URL, пытаемся получить его из GET-параметров
        if not category_pk:
            category_pk = self.request.GET.get('category')

        if not category_pk:
            raise Http404("Идентификатор категории не указан.")

        return category_pk

    def get_category(self):
        """Получает объект категории по найденному ID."""
        category_pk = self.get_category_id()
        return get_object_or_404(Category, pk=category_pk)

    def get_queryset(self):
        """
        Формирует QuerySet, фильтруя по категории и применяя
        дополнительные фильтры по марке/модели/поколению из GET-параметров.
        """
        category = self.get_category()
        queryset = super().get_queryset().filter(category=category, is_active=True)
        selected_make_pk = self.request.GET.get('make')
        selected_model_pk = self.request.GET.get('model')
        selected_generation_pk = self.request.GET.get('generation')
        filters = Q()
        if selected_make_pk:
            filters &= Q(car_generations__model__make__pk=selected_make_pk)
        if selected_model_pk:
            filters &= Q(car_generations__model__pk=selected_model_pk)
        if selected_generation_pk:
            filters &= Q(car_generations__pk=selected_generation_pk)
        if filters:
            queryset = queryset.filter(filters).distinct()
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст объект категории и ПОЛНЫЕ списки для боковой панели фильтрации.
        """
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        context['category'] = category
        selected_make_pk = self.request.GET.get('make')
        selected_model_pk = self.request.GET.get('model')
        available_makes = CarMake.objects.all().order_by('name')
        context['car_makes'] = available_makes
        context['car_models'] = []
        context['car_generations'] = []

        if selected_make_pk:
            try:
                models = CarModel.objects.filter(
                    make__pk=selected_make_pk
                ).order_by('name')
                context['car_models'] = models
            except Exception:
                pass

        if selected_model_pk:
            try:
                generations = CarGeneration.objects.filter(
                    model__pk=selected_model_pk
                ).order_by('name')
                context['car_generations'] = generations
            except Exception:
                pass
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
        queryset = Part.objects.filter(donor_generation=self.generation_obj, is_active=True)
        category_pk = self.request.GET.get('category')
        if category_pk:
            queryset = queryset.filter(category__pk=category_pk)
        return queryset.order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_generation'] = self.generation_obj
        context['categories'] = Category.objects.filter(part__donor_generation=self.generation_obj).distinct().order_by('name')   #Фильтруем категории, чтобы показать только те, которые есть в этом поколении
        selected_category_pk = self.request.GET.get('category')
        if selected_category_pk:
            context['selected_category_pk'] = selected_category_pk
        return context


class DonorDetailView(DetailView):
    """
    Отображает детали конкретной машины-донора: полную галерею и список
    всех запчастей, снятых с нее, с возможностью фильтрации по категории.
    """
    model = DonorVehicle
    template_name = 'main/donor_detail.html'
    context_object_name = 'donor'

    def get_queryset(self):

        # Оптимизация запросов: получаем Make/Model/Generation и все изображения
        return super().get_queryset().select_related('generation__model__make').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        donor = self.object    #Полученный DonorVehicle
        category_id = self.request.GET.get('category_id')
        parts_queryset = donor.parts.filter(is_active=True).select_related('category').prefetch_related('images')
        if category_id:
            parts_queryset = parts_queryset.filter(category_id=category_id)
        context['parts_list'] = parts_queryset.order_by('category__name', 'title')
        categories_with_count = Category.objects.filter(part__donor_vehicle=donor,part__is_active=True).annotate(part_count=Count('part')).order_by('name')
        context['categories'] = categories_with_count
        context['total_parts_count'] = donor.parts.filter(is_active=True).count()
        context['page_title'] = f"Донор: {donor.generation.model.make.name} {donor.generation.model.name} ({donor.title})"
        return context