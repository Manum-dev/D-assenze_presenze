from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsParticipant
from .serializers import ParticipantProfileSerializer

from .serializers import UserSerializer

permission_classes = [IsAuthenticated]

class ParticipantProfileView(APIView):
    """
    Gestione profilo del partecipante.
    
    GET  /api/participant/profile/  → Visualizza il proprio profilo
    PUT  /api/participant/profile/  → Aggiorna il proprio profilo
    """
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get(self, request):
        """Visualizza il profilo del partecipante loggato"""
        serializer = ParticipantProfileSerializer(request.user)
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    def put(self, request):
        """Aggiorna il profilo del partecipante loggato"""
        serializer = ParticipantProfileSerializer(
            request.user,
            data=request.data,
            partial=True  # Permette aggiornamenti parziali
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "success": True,
            "message": "Profilo aggiornato con successo.",
            "data": serializer.data
        })


class CurrentUserView(APIView):
    """
    Restituisce l'utente corrente (loggato).
    
    GET /api/me/  → Info utente corrente
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Restituisce i dati dell'utente loggato"""
        from .serializers import UserSerializer
        serializer = UserSerializer(request.user)
        return Response({
            "success": True,
            "data": serializer.data
        })
