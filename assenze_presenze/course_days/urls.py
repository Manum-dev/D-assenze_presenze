from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseDayViewSet

router = DefaultRouter()
router.register(r'admin/course-days', CourseDayViewSet, basename='course-day')

urlpatterns = [
    path('', include(router.urls)),
]