from rest_framework import serializers
from .models import CourseDay


class CourseDaySerializer(serializers.ModelSerializer):
    """
    Serializer per le giornate di corso.
    Usato per CRUD completo (admin).
    """
    class Meta:
        model = CourseDay
        fields = [
            'id',
            'date',
            'description',
            'is_holiday',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_date(self, value):
        """Verifica che la data non sia duplicata"""
        instance = getattr(self, 'instance', None)
        queryset = CourseDay.objects.filter(date=value)
        
        # Se stiamo aggiornando, escludi il record corrente
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Esiste già una giornata di corso per questa data."
            )
        return value