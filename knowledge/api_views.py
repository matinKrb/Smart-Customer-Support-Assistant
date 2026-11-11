from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import KnowledgeItem
from .serializers import KnowledgeItemSerializer


class KnowledgeItemViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeItem.objects.all()
    serializer_class = KnowledgeItemSerializer
    permission_classes = [IsAuthenticated]