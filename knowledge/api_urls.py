from rest_framework.routers import DefaultRouter
from .api_views import KnowledgeItemViewSet

router = DefaultRouter()
router.register('knowledge-items', KnowledgeItemViewSet, basename='knowledge-item')

urlpatterns = router.urls