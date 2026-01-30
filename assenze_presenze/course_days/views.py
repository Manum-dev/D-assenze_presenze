from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CourseDay
from .serializers import CourseDaySerializer
from admins.permissions import IsAdmin


class CourseDayViewSet(viewsets.ModelViewSet):
    """
    ViewSet per la gestione delle giornate di corso.
    
    Solo gli admin possono:
    - GET    /api/admin/course-days/          → Lista tutte le giornate
    - POST   /api/admin/course-days/          → Crea nuova giornata
    - GET    /api/admin/course-days/{id}/     → Dettaglio giornata
    - PUT    /api/admin/course-days/{id}/     → Modifica giornata
    - DELETE /api/admin/course-days/{id}/     → Elimina giornata
    """
    queryset = CourseDay.objects.all()
    serializer_class = CourseDaySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['date', 'is_holiday']
    search_fields = ['description']
    
    def list(self, request, *args, **kwargs):
        """Lista giornate con response formattata"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Dettaglio giornata con response formattata"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Crea giornata con response formattata"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "success": True,
            "message": "Giornata creata con successo",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Modifica giornata con response formattata"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "message": "Giornata aggiornata con successo",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Elimina giornata con response formattata"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Giornata eliminata con successo"
        }, status=status.HTTP_200_OK)