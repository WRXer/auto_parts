from django.core.exceptions import ValidationError
from django.db import models


NULLABLE = {'blank': True, 'null': True}


class CarMake(models.Model):
    """
    Марка автомобиля
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Марка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Марка автомобиля'
        verbose_name_plural = 'Марки автомобилей'

class CarModel(models.Model):
    """
    Модель автомобиля
    """
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models', verbose_name='Марка')
    name = models.CharField(max_length=100, verbose_name='Модель')

    def __str__(self):
        return f'{self.make.name} {self.name}'

    class Meta:
        verbose_name = 'Модель автомобиля'
        verbose_name_plural = 'Модели автомобилей'
        unique_together = ('make', 'name')    #Модель уникальна внутри Марки

class CarGeneration(models.Model):
    """
    Поколение или Модификация (например, Audi A6 C7 2011-2018)
    """
    model = models.ForeignKey(
        CarModel,
        on_delete=models.CASCADE,
        related_name='generations',
        verbose_name='Модель'
    )
    name = models.CharField(max_length=255, verbose_name='Название поколения/модификации')
    year_start = models.PositiveSmallIntegerField(verbose_name='Год начала выпуска', **NULLABLE)
    year_end = models.PositiveSmallIntegerField(verbose_name='Год окончания выпуска', **NULLABLE)

    def __str__(self):
        return f'{self.model.make.name} {self.model.name} ({self.name})'

    class Meta:
        verbose_name = 'Поколение/Модификация'
        verbose_name_plural = 'Поколения/Модификации'
        ordering = ('model__make__name', 'model__name', 'year_start')

class Category(models.Model):
    """
    Категория запчасти (Двигатель, Кузов, Салон)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Название категории')
    description = models.TextField(verbose_name='Описание', **NULLABLE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория запчасти'
        verbose_name_plural = 'Категории запчастей'

class Part(models.Model):
    """
    Основное объявление о продаже запчасти
    """
    CONDITION_CHOICES = (
        ('used', 'Б/У'),
        ('new', 'Новая'),
        ('restored', 'Восстановленная'),
    )

    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')    #Связи с другими моделями

    part_id = models.CharField(max_length=50,verbose_name='Внутренний артикул продавца',unique=True,**NULLABLE)
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Подробное описание')
    part_number = models.CharField(max_length=100, verbose_name='OEM/Артикул', **NULLABLE)
    donor_generation = models.ForeignKey('CarGeneration',on_delete=models.PROTECT,related_name='donor_parts',verbose_name='Автомобиль-донор (Поколение/Модификация)')
    car_generations = models.ManyToManyField('CarGeneration',related_name='compatible_parts', verbose_name='Совместимые модификации/поколения', blank=True)    #Связь с совместимыми машинами (куда подходит запчасть)
    donor_vehicle = models.ForeignKey('DonorVehicle',on_delete=models.SET_NULL,blank=True,null=True,related_name='parts',verbose_name="Конкретная машина-донор (поступление)",help_text="С какой конкретной машины снята эта запчасть")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='used', verbose_name='Состояние')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Запчасть (Объявление)'
        verbose_name_plural = 'Запчасти (Объявления)'
        ordering = ('-created_at',)

    def get_main_image_source(self):
        """
        Возвращает главное изображение (is_main=True) или первое
        изображение, если главное не отмечено.
        """
        main_img = self.images.filter(is_main=True).first()    #Сначала ищем изображение, помеченное как главное
        if main_img:
            return main_img.get_image_source()
        first_image = self.images.first()
        return first_image.get_image_source() if first_image else None


class PartImage(models.Model):
    """
    Изображения для объявления
    """
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='images', verbose_name='Запчасть')
    image = models.ImageField(upload_to='part_images/', verbose_name='Изображение', blank=True, null=True)
    image_url = models.URLField(max_length=500,verbose_name='URL Изображения', blank=True, null=True)
    is_main = models.BooleanField(default=False, verbose_name='Главное фото')

    class Meta:
        verbose_name = 'Изображение запчасти'
        verbose_name_plural = 'Изображения запчастей'

    def get_image_source(self) -> str | None:
        """
        Возвращает актуальный путь или URL для отображения.
        """
        if self.image:
            return self.image.url   #Django добавляет .url к ImageField
        if self.image_url:
            return self.image_url
        return None

    def clean(self):
        """
        Проверяет, что заполнено только одно из полей.
        """
        has_file = bool(self.image)
        has_url = bool(self.image_url)

        if has_file and has_url:
            raise ValidationError(
                'Нельзя заполнять одновременно "Файл Изображения" и "Внешний URL Изображения".'
            )


class DonorVehicle(models.Model):
    """
    Представляет КОНКРЕТНЫЙ автомобиль, поступивший в разбор.
    """
    TRANSMISSION_CHOICES = [
        ('AT', 'Автоматическая'),
        ('MT', 'Механическая')]

    generation = models.ForeignKey(CarGeneration, on_delete=models.PROTECT,verbose_name="Модификация (Тип авто)")
    title = models.CharField(max_length=255,verbose_name="Название/Описание поступления (для себя)",help_text="Напр: 'Синий, 2.0л, пробег 140т.км' или 'Поступление #2'")    #Название или описание конкретного поступления для отображения на главной
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name="Цвет")
    production_year = models.IntegerField(blank=True, null=True, verbose_name="Год выпуска")
    engine_details = models.CharField(max_length=255, blank=True, null=True, verbose_name="Детали двигателя (объем/модель)")
    description = models.TextField(blank=True, null=True, verbose_name="Полное описание донора")
    transmission_type = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES, blank=True, null=True,verbose_name="Тип КПП")
    arrival_date = models.DateField(auto_now_add=True,verbose_name="Дата поступления")

    class Meta:
        verbose_name = "Машина-донор (поступление)"
        verbose_name_plural = "Машины-доноры (поступления)"
        ordering = ['-arrival_date']

    def __str__(self):
        return f"{self.generation.model.make.name} {self.generation.model.name} ({self.title})"

    def get_main_image_source(self):
        """
        Возвращает главное изображение или первое изображение, если главное не отмечено.
        """
        main_img = self.images.filter(is_main=True).first()
        if main_img:
            return main_img.get_image_source()
        first_image = self.images.first()
        return first_image.get_image_source() if first_image else None


class DonorVehicleImage(models.Model):
    """
    Изображения для конкретного автомобиля-донора.
    """
    donor_vehicle = models.ForeignKey(DonorVehicle,on_delete=models.CASCADE,related_name='images',verbose_name='Машина-донор')
    image = models.ImageField(upload_to='donor_vehicle_images/', verbose_name='Изображение', blank=True, null=True)
    image_url = models.URLField(max_length=500,verbose_name='Внешний URL Изображения',blank=True, null=True)
    is_main = models.BooleanField(default=False, verbose_name='Главное фото')

    class Meta:
        verbose_name = 'Изображение донора'
        verbose_name_plural = 'Изображения донора'

    def get_image_source(self) -> str | None:
        """
        Возвращает актуальный источник изображения (URL или путь к загруженному файлу).
        """
        if self.image:
            return self.image.url    #Возвращает URL загруженного файла
        if self.image_url:
            return self.image_url    #Возвращает внешний URL
        return None

    def clean(self):
        """
        Проверяет, что заполнено только одно из полей.
        """
        has_file = bool(self.image)
        has_url = bool(self.image_url)

        if has_file and has_url:
            raise ValidationError(
                'Нельзя заполнять одновременно "Файл Изображения" и "Внешний URL Изображения".'
            )
