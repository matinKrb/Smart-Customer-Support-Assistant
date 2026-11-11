from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Conversation
from .serializers import ConversationListSerializer, ConversationDetailSerializer


class ConversationListView(generics.ListAPIView):
    queryset = Conversation.objects.all().order_by('-updated_at')
    serializer_class = ConversationListSerializer
    permission_classes = [IsAuthenticated]


class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'


from rest_framework.views import APIView
from rest_framework.response import Response


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_conversations = Conversation.objects.count()

        handoff_count = Conversation.objects.filter(
            status__in=[Conversation.Status.WAITING_FOR_HUMAN, Conversation.Status.HUMAN_HANDLING]
        ).count()

        error_conversations = Conversation.objects.filter(consecutive_errors__gt=0).count()

        return Response({
            "total_conversations": total_conversations,
            "handoff_count": handoff_count,
            "conversations_with_errors": error_conversations,
        })