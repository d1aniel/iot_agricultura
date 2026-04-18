from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Riego
from .serializers import RiegoSerializer

class RiegoViewSet(viewsets.ModelViewSet):
    queryset = Riego.objects.all()
    serializer_class = RiegoSerializer

    @action(detail=False, methods=['get'])
    def latest(self, request):
        ultimo = Riego.objects.order_by('-fecha').first()
        if ultimo:
            serializer = self.get_serializer(ultimo)
            return Response(serializer.data)
        return Response({"mensaje": "No hay comandos"})