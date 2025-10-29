from rest_framework import generics
from spare_parts.models import Part
from spare_parts.serializers import PartSerializer


class PartListAPIView(generics.ListAPIView):
    """
    Список запчастей
    """
    serializer_class = PartSerializer
    queryset = Part.objects.all()


class PartRetieveAPIView(generics.RetrieveAPIView):
    """
    Вывод одной запчасти
    """
    serializer_class = PartSerializer
    queryset = Part.objects.all()