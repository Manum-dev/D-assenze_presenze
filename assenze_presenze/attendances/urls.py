from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminAttendanceViewSet,
    ParticipantAttendanceListView,
    ParticipantStatsView
)

# Router per ViewSet admin
router = DefaultRouter()
router.register(r'admin/attendances', AdminAttendanceViewSet, basename='attendance')

urlpatterns = [
    # Endpoint admin (CRUD + bulk + link-user)
    path('', include(router.urls)),
    
    # Endpoint partecipante (solo lettura)
    path('participant/attendances/', ParticipantAttendanceListView.as_view(), name='participant-attendances'),
    path('participant/stats/', ParticipantStatsView.as_view(), name='participant-stats'),
]