from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer per la registrazione utenti.
    Il primo utente registrato diventa automaticamente ADMIN.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text='Minimo 8 caratteri'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'password_confirm'
        ]
    
    def validate_email(self, value):
        """Verifica che l'email non sia già registrata"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email già registrata.")
        return value.lower()
    
    def validate_username(self, value):
        """Verifica che l'username non sia già in uso"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username già in uso.")
        return value
    
    def validate(self, data):
        """Verifica che le password coincidano"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Le password non coincidono."
            })
        return data
    
    def create(self, validated_data):
        """Crea l'utente. Il primo diventa ADMIN."""
        validated_data.pop('password_confirm')
        
        # Primo utente = ADMIN, tutti gli altri = PARTICIPANT
        is_first_user = not CustomUser.objects.exists()
        role = CustomUser.Role.ADMIN if is_first_user else CustomUser.Role.PARTICIPANT
        
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            role=role
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer per il login.
    Autentica l'utente tramite email e password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """Autentica l'utente"""
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        if not email or not password:
            raise serializers.ValidationError("Email e password sono obbligatori.")
        
        # Autentica usando l'email come username
        user = authenticate(username=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Credenziali non valide.")
        
        if not user.is_active:
            raise serializers.ValidationError("Account disattivato.")
        
        data['user'] = user
        return data