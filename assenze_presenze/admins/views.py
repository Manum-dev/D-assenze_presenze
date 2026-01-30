from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from course_days.models import CourseDay
from attendances.models import Attendance
from .permissions import IsAdmin
from .serializers import (
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    AdminUserCreateSerializer
)


class AdminDashboardView(APIView):
    """
    Dashboard admin con statistiche generali.
    
    GET /api/admin/dashboard/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Statistiche generali
        stats = {
            'total_users': CustomUser.objects.count(),
            'total_admins': CustomUser.objects.filter(role=CustomUser.Role.ADMIN).count(),
            'total_participants': CustomUser.objects.filter(role=CustomUser.Role.PARTICIPANT).count(),
            'total_course_days': CourseDay.objects.count(),
            'total_attendances': Attendance.objects.count(),
        }
        
        # Ultimi 5 utenti registrati
        recent_users = CustomUser.objects.order_by('-created_at')[:5]
        
        return Response({
            "success": True,
            "data": {
                "stats": stats,
                "recent_users": AdminUserSerializer(recent_users, many=True).data
            }
        })


class AdminUserListCreateView(APIView):
    """
    Lista e creazione utenti.
    
    GET  /api/admin/users/          → Lista tutti gli utenti
    POST /api/admin/users/          → Crea nuovo utente
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Lista utenti con filtri opzionali"""
        queryset = CustomUser.objects.all().order_by('-created_at')
        
        # Filtro per ruolo
        role = request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filtro per stato attivo
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Ricerca per email o nome
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        serializer = AdminUserSerializer(queryset, many=True)
        
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })
    
    def post(self, request):
        """Crea nuovo utente"""
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "success": True,
            "message": "Utente creato con successo.",
            "data": AdminUserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class AdminUserDetailView(RetrieveUpdateDestroyAPIView):
    """
    Dettaglio, modifica ed eliminazione utente.
    
    GET    /api/admin/users/{id}/   → Dettaglio utente
    PUT    /api/admin/users/{id}/   → Modifica utente
    PATCH  /api/admin/users/{id}/   → Modifica parziale
    DELETE /api/admin/users/{id}/   → Elimina utente
    """
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_url_kwarg = 'user_id'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdminUserUpdateSerializer
        return AdminUserSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            "success": True,
            "message": "Utente aggiornato con successo.",
            "data": AdminUserSerializer(instance).data
        })
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Impedisce eliminazione di se stesso
        if user == request.user:
            return Response({
                "success": False,
                "error": "Non puoi eliminare te stesso."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Impedisce eliminazione ultimo admin
        if user.is_admin():
            admin_count = CustomUser.objects.filter(role=CustomUser.Role.ADMIN).count()
            if admin_count == 1:
                return Response({
                    "success": False,
                    "error": "Non puoi eliminare l'unico admin del sistema."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        
        return Response({
            "success": True,
            "message": "Utente eliminato con successo."
        }, status=status.HTTP_200_OK)


class PromoteUserView(APIView):
    """
    Promuove un partecipante ad admin.
    
    POST /api/admin/users/{id}/promote/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "error": "Utente non trovato."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_admin():
            return Response({
                "success": False,
                "error": "L'utente è già amministratore."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.promote_to_admin()
        
        return Response({
            "success": True,
            "message": f"{user.email} è stato promosso ad amministratore.",
            "data": AdminUserSerializer(user).data
        })


class DemoteUserView(APIView):
    """
    Rimuove i privilegi admin da un utente.
    
    POST /api/admin/users/{id}/demote/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "error": "Utente non trovato."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_participant():
            return Response({
                "success": False,
                "error": "L'utente non è amministratore."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Impedisce auto-rimozione se ultimo admin
        if user == request.user:
            admin_count = CustomUser.objects.filter(role=CustomUser.Role.ADMIN).count()
            if admin_count == 1:
                return Response({
                    "success": False,
                    "error": "Sei l'unico admin. Promuovi qualcun altro prima di rimuoverti."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        user.demote_to_participant()
        
        return Response({
            "success": True,
            "message": f"{user.email} non è più amministratore.",
            "data": AdminUserSerializer(user).data
        })


class AdminListView(ListAPIView):
    """
    Lista solo gli admin.
    
    GET /api/admin/admins/
    """
    queryset = CustomUser.objects.filter(role=CustomUser.Role.ADMIN).order_by('-created_at')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })


class ParticipantListView(ListAPIView):
    """
    Lista solo i partecipanti.
    
    GET /api/admin/participants/
    """
    queryset = CustomUser.objects.filter(role=CustomUser.Role.PARTICIPANT).order_by('-created_at')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })
