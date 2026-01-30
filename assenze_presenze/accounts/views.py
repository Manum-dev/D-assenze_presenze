from django.shortcuts import render

# Create your views here.

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from users.serializers import UserSerializer


class RegisterView(APIView):
    """
    Registrazione nuovo utente.
    
    POST /api/auth/register/
    
    Il primo utente registrato diventa automaticamente ADMIN.
    Tutti gli altri utenti diventano PARTICIPANT.
    
    Request body:
    {
        "email": "user@example.com",
        "username": "username",
        "first_name": "Nome",
        "last_name": "Cognome",
        "password": "password123",
        "password_confirm": "password123"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Genera i token JWT
        refresh = RefreshToken.for_user(user)
        
        # Messaggio personalizzato per admin
        if user.is_admin():
            message = "Registrazione completata. Sei l'amministratore del sistema."
        else:
            message = "Registrazione completata."
        
        return Response({
            "success": True,
            "message": message,
            "data": {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Login utente.
    
    POST /api/auth/login/
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Genera i token JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "success": True,
            "message": "Login effettuato con successo.",
            "data": {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Logout utente (invalida il refresh token).
    
    POST /api/auth/logout/
    
    Request body:
    {
        "refresh": "refresh_token_here"
    }
    """
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    "success": False,
                    "error": "Refresh token richiesto."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                "success": True,
                "message": "Logout effettuato con successo."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": "Token non valido."
            }, status=status.HTTP_400_BAD_REQUEST)