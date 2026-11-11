from django.urls import path
from .api_views import ConversationListView, ConversationDetailView, DashboardStatsView

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:uuid>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]