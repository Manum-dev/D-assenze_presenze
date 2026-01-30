from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer base per gli utenti.
    Usato per visualizzazione generale.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'role_display',
            'phone',
            'birth_date',
            'created_at'
        ]
        read_only_fields = ['id', 'role', 'created_at']


class ParticipantProfileSerializer(serializers.ModelSerializer):
    """
    Serializer per il profilo del partecipante.
    
    Campi modificabili: first_name, last_name, phone, birth_date
    Campi in sola lettura: id, email, username, role, created_at
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'role_display',
            'phone',
            'birth_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'email',
            'username',
            'role',
            'role_display',
            'created_at',
            'updated_at'
        ]
    
    def validate_phone(self, value):
        """Validazione numero di telefono"""
        if value:
            # Rimuovi spazi e caratteri speciali
            cleaned = ''.join(c for c in value if c.isdigit() or c == '+')
            if len(cleaned) < 6:
                raise serializers.ValidationError(
                    "Numero di telefono troppo corto."
                )
        return value