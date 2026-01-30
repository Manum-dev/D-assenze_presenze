from rest_framework import serializers
from users.models import CustomUser


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Serializer per visualizzazione utenti (usato dall'admin).
    Include il conteggio delle presenze.
    """
    attendances_count = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
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
            'phone',
            'birth_date',
            'is_active',
            'attendances_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_attendances_count(self, obj):
        """Conta le presenze dell'utente"""
        if hasattr(obj, 'attendances'):
            return obj.attendances.count()
        return 0
    
    def get_full_name(self, obj):
        """Restituisce nome completo"""
        return f"{obj.first_name} {obj.last_name}".strip()


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer per modifica utenti (usato dall'admin).
    L'admin può modificare questi campi.
    """
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'phone',
            'birth_date',
            'is_active'
        ]


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer per creazione utenti da parte dell'admin.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'role',
            'phone',
            'birth_date'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer per le statistiche della dashboard"""
    total_users = serializers.IntegerField()
    total_admins = serializers.IntegerField()
    total_participants = serializers.IntegerField()
    total_course_days = serializers.IntegerField()
    total_attendances = serializers.IntegerField()
    recent_users = AdminUserSerializer(many=True)