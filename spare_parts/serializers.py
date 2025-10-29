from rest_framework import serializers
from spare_parts.models import CarGeneration, Part


class CarGenerationSimpleSerializer(serializers.ModelSerializer):
    """
    Для отображения модификации/поколения в списке
    """
    car_model_name = serializers.CharField(source='car_model.name', read_only=True)
    car_make_name = serializers.CharField(source='car_model.make.name', read_only=True)

    class Meta:
        model = CarGeneration
        fields = ('id', 'car_make_name', 'car_model_name', 'name', 'year_start', 'year_end')

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = '__all__'

