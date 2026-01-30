from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from .models import Attendance
from .serializers import (
    AttendanceSerializer,
    ParticipantAttendanceSerializer,
    BulkAttendanceSerializer,
    LinkUserSerializer,
    AttendanceStatsSerializer
)
from admins.permissions import IsAdmin, IsParticipant
from course_days.models import CourseDay


class AdminAttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet per la gestione delle presenze (solo admin).
    
    Endpoints:
    - GET    /api/admin/attendances/              → Lista tutte le presenze
    - POST   /api/admin/attendances/              → Crea nuova presenza
    - GET    /api/admin/attendances/{id}/         → Dettaglio presenza
    - PUT    /api/admin/attendances/{id}/         → Modifica presenza
    - DELETE /api/admin/attendances/{id}/         → Elimina presenza
    - POST   /api/admin/attendances/bulk/         → Crea presenze multiple
    - POST   /api/admin/attendances/link-user/    → Collega utente a presenze
    """
    queryset = Attendance.objects.select_related('course_day', 'user').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['course_day', 'user', 'status', 'participant_identifier']
    search_fields = ['participant_identifier', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['course_day__date', 'participant_identifier', 'status', 'created_at']
    
    def list(self, request, *args, **kwargs):
        """Lista presenze con filtri e response formattata"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtro aggiuntivo per mese (es: ?month=2025-01)
        month = request.query_params.get('month')
        if month:
            try:
                year, m = month.split('-')
                queryset = queryset.filter(
                    course_day__date__year=int(year),
                    course_day__date__month=int(m)
                )
            except ValueError:
                pass
        
        # Paginazione
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Dettaglio presenza"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Crea nuova presenza"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "success": True,
            "message": "Presenza registrata con successo.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Modifica presenza"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "message": "Presenza aggiornata con successo.",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Elimina presenza"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Presenza eliminata con successo."
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """
        Crea presenze multiple per una giornata.
        
        POST /api/admin/attendances/bulk/
        
        Request body:
        {
            "course_day_id": 1,
            "attendances": [
                {"participant_identifier": "mario@test.com", "status": "PRESENT"},
                {"participant_identifier": "lucia@test.com", "status": "ABSENT"},
                {"participant_identifier": "paolo@test.com", "status": "EXCUSED", "notes": "Certificato medico"}
            ]
        }
        """
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        course_day_id = serializer.validated_data['course_day_id']
        attendances_data = serializer.validated_data['attendances']
        
        created = []
        updated = []
        
        for item in attendances_data:
            attendance, was_created = Attendance.objects.update_or_create(
                course_day_id=course_day_id,
                participant_identifier=item['participant_identifier'],
                defaults={
                    'status': item['status'],
                    'notes': item.get('notes', '')
                }
            )
            if was_created:
                created.append(attendance)
            else:
                updated.append(attendance)
        
        all_attendances = created + updated
        
        return Response({
            "success": True,
            "message": f"Create {len(created)} nuove presenze, aggiornate {len(updated)} esistenti.",
            "data": {
                "created_count": len(created),
                "updated_count": len(updated),
                "attendances": AttendanceSerializer(all_attendances, many=True).data
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='link-user')
    def link_user(self, request):
        """
        Collega un utente registrato alle sue presenze esistenti.
        
        POST /api/admin/attendances/link-user/
        
        Request body:
        {
            "user_id": 5,
            "participant_identifier": "mario@test.com"
        }
        """
        serializer = LinkUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        identifier = serializer.validated_data['participant_identifier']
        
        # Aggiorna tutte le presenze con quell'identifier
        updated_count = Attendance.objects.filter(
            participant_identifier=identifier
        ).update(user_id=user_id)
        
        if updated_count == 0:
            return Response({
                "success": False,
                "error": f"Nessuna presenza trovata con identificativo '{identifier}'."
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "success": True,
            "message": f"Collegate {updated_count} presenze all'utente.",
            "data": {
                "updated_count": updated_count,
                "user_id": user_id,
                "participant_identifier": identifier
            }
        })
    
    @action(detail=False, methods=['get'], url_path='by-course-day/(?P<course_day_id>[^/.]+)')
    def by_course_day(self, request, course_day_id=None):
        """
        Lista presenze per una specifica giornata.
        
        GET /api/admin/attendances/by-course-day/{course_day_id}/
        """
        attendances = self.get_queryset().filter(course_day_id=course_day_id)
        serializer = self.get_serializer(attendances, many=True)
        
        # Statistiche giornata
        stats = {
            'total': attendances.count(),
            'present': attendances.filter(status=Attendance.Status.PRESENT).count(),
            'absent': attendances.filter(status=Attendance.Status.ABSENT).count(),
            'excused': attendances.filter(status=Attendance.Status.EXCUSED).count(),
        }
        
        return Response({
            "success": True,
            "course_day_id": course_day_id,
            "stats": stats,
            "data": serializer.data
        })


class ParticipantAttendanceListView(APIView):
    """
    Lista delle presenze del partecipante loggato.
    
    GET /api/participant/attendances/
    
    Il partecipante può vedere SOLO le proprie presenze.
    Non può modificare nulla.
    """
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get(self, request):
        """Lista presenze del partecipante"""
        # Cerca presenze tramite user ID o participant_identifier (email)
        attendances = Attendance.objects.filter(
            Q(user=request.user) | Q(participant_identifier=request.user.email)
        ).select_related('course_day').order_by('course_day__date')
        
        # Filtro opzionale per mese
        month = request.query_params.get('month')
        if month:
            try:
                year, m = month.split('-')
                attendances = attendances.filter(
                    course_day__date__year=int(year),
                    course_day__date__month=int(m)
                )
            except ValueError:
                pass
        
        # Filtro opzionale per stato
        status_filter = request.query_params.get('status')
        if status_filter:
            attendances = attendances.filter(status=status_filter)
        
        serializer = ParticipantAttendanceSerializer(attendances, many=True)
        
        return Response({
            "success": True,
            "count": attendances.count(),
            "data": serializer.data
        })


class ParticipantStatsView(APIView):
    """
    Statistiche delle presenze del partecipante.
    
    GET /api/participant/stats/
    
    La percentuale è calcolata SOLO sulle giornate passate.
    I giustificati (EXCUSED) contano come presenza.
    """
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get(self, request):
        """Calcola statistiche presenze"""
        today = timezone.now().date()
        
        # Giornate di corso passate (escluse future)
        past_course_days = CourseDay.objects.filter(date__lte=today)
        total_past_days = past_course_days.count()
        
        # Giornate future
        future_course_days = CourseDay.objects.filter(date__gt=today)
        total_future_days = future_course_days.count()
        
        # Presenze dell'utente (solo giorni passati)
        user_attendances = Attendance.objects.filter(
            Q(user=request.user) | Q(participant_identifier=request.user.email),
            course_day__date__lte=today
        )
        
        # Conteggi per stato
        present_count = user_attendances.filter(status=Attendance.Status.PRESENT).count()
        absent_count = user_attendances.filter(status=Attendance.Status.ABSENT).count()
        excused_count = user_attendances.filter(status=Attendance.Status.EXCUSED).count()
        
        # Calcolo percentuale
        # PRESENT + EXCUSED contano come presenza
        if total_past_days > 0:
            attendance_percentage = round(
                ((present_count + excused_count) / total_past_days) * 100,
                2
            )
        else:
            attendance_percentage = 0.0
        
        # Breakdown mensile (opzionale)
        monthly_breakdown = []
        months = user_attendances.dates('course_day__date', 'month')
        for month in months:
            month_attendances = user_attendances.filter(
                course_day__date__year=month.year,
                course_day__date__month=month.month
            )
            month_days = past_course_days.filter(
                date__year=month.year,
                date__month=month.month
            ).count()
            
            month_present = month_attendances.filter(status=Attendance.Status.PRESENT).count()
            month_excused = month_attendances.filter(status=Attendance.Status.EXCUSED).count()
            
            month_percentage = round(
                ((month_present + month_excused) / month_days) * 100, 2
            ) if month_days > 0 else 0.0
            
            monthly_breakdown.append({
                'month': month.strftime('%Y-%m'),
                'total_days': month_days,
                'present': month_present,
                'absent': month_attendances.filter(status=Attendance.Status.ABSENT).count(),
                'excused': month_excused,
                'percentage': month_percentage
            })
        
        return Response({
            "success": True,
            "data": {
                "total_course_days_past": total_past_days,
                "total_course_days_future": total_future_days,
                "present": present_count,
                "absent": absent_count,
                "excused": excused_count,
                "attendance_percentage": attendance_percentage,
                "monthly_breakdown": monthly_breakdown
            }
        })
