from rest_framework import serializers
from .models import Attendance
from users.serializers import UserSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer completo per le presenze.
    Usato dall'admin per CRUD.
    """
    # Campi extra in sola lettura
    course_day_date = serializers.DateField(
        source='course_day.date',
        read_only=True
    )
    course_day_description = serializers.CharField(
        source='course_day.description',
        read_only=True
    )
    user_email = serializers.EmailField(
        source='user.email',
        read_only=True
    )
    user_full_name = serializers.CharField(
        source='user.get_full_name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Attendance
        fields = [
            'id',
            'user',
            'user_email',
            'user_full_name',
            'course_day',
            'course_day_date',
            'course_day_description',
            'participant_identifier',
            'status',
            'status_display',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validazione: verifica unicità presenza per giornata"""
        course_day = data.get('course_day')
        participant_identifier = data.get('participant_identifier')
        instance = getattr(self, 'instance', None)
        
        if course_day and participant_identifier:
            queryset = Attendance.objects.filter(
                course_day=course_day,
                participant_identifier=participant_identifier
            )
            # Se stiamo aggiornando, escludi il record corrente
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    "participant_identifier": "Presenza già registrata per questa giornata."
                })
        
        return data


class ParticipantAttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer per visualizzazione presenze del partecipante.
    Solo campi in lettura, nessuna modifica permessa.
    """
    date = serializers.DateField(
        source='course_day.date',
        read_only=True
    )
    description = serializers.CharField(
        source='course_day.description',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    is_present = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id',
            'date',
            'description',
            'status',
            'status_display',
            'is_present',
            'notes'
        ]
        # Tutti i campi in sola lettura!
        read_only_fields = fields


class BulkAttendanceItemSerializer(serializers.Serializer):
    """
    Serializer per singola presenza nel bulk create.
    """
    participant_identifier = serializers.CharField(
        max_length=255,
        help_text='Email o codice identificativo'
    )
    status = serializers.ChoiceField(
        choices=Attendance.Status.choices,
        default=Attendance.Status.ABSENT
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default=''
    )


class BulkAttendanceSerializer(serializers.Serializer):
    """
    Serializer per creazione multipla di presenze.
    Permette di registrare tutte le presenze di una giornata in una volta.
    """
    course_day_id = serializers.IntegerField(
        help_text='ID della giornata di corso'
    )
    attendances = BulkAttendanceItemSerializer(
        many=True,
        help_text='Lista delle presenze da registrare'
    )
    
    def validate_course_day_id(self, value):
        """Verifica che la giornata esista"""
        from course_days.models import CourseDay
        if not CourseDay.objects.filter(id=value).exists():
            raise serializers.ValidationError("Giornata di corso non trovata.")
        return value
    
    def validate_attendances(self, value):
        """Verifica che ci sia almeno una presenza"""
        if not value:
            raise serializers.ValidationError("Inserire almeno una presenza.")
        return value


class LinkUserSerializer(serializers.Serializer):
    """
    Serializer per collegare un utente alle sue presenze.
    """
    user_id = serializers.IntegerField(
        help_text='ID dell\'utente da collegare'
    )
    participant_identifier = serializers.CharField(
        max_length=255,
        help_text='Identificativo usato per le presenze'
    )
    
    def validate_user_id(self, value):
        """Verifica che l'utente esista"""
        from users.models import CustomUser
        if not CustomUser.objects.filter(id=value).exists():
            raise serializers.ValidationError("Utente non trovato.")
        return value


class AttendanceStatsSerializer(serializers.Serializer):
    """
    Serializer per le statistiche delle presenze.
    """
    total_course_days_past = serializers.IntegerField()
    total_course_days_future = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    excused = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
    
    # Dettaglio per mese (opzionale)
    monthly_breakdown = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )