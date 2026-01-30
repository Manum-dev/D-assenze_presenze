from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin panel per la gestione delle presenze"""
    
    # Colonne nella lista
    list_display = [
        'participant_identifier',
        'course_day',
        'status',
        'user',
        'created_at'
    ]
    
    # Filtri laterali
    list_filter = ['status', 'course_day', 'course_day__date']
    
    # Campi di ricerca
    search_fields = [
        'participant_identifier',
        'user__email',
        'user__first_name',
        'user__last_name',
        'notes'
    ]
    
    # Ordinamento default
    ordering = ['-course_day__date', 'participant_identifier']
    
    # Campi in sola lettura
    readonly_fields = ['created_at', 'updated_at']
    
    # Organizzazione campi nel form
    fieldsets = (
        ('Informazioni Principali', {
            'fields': ('participant_identifier', 'course_day', 'status')
        }),
        ('Collegamento Utente', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Note', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Autocomplete per relazioni
    autocomplete_fields = ['user', 'course_day']
    
    # Azioni bulk
    actions = ['mark_as_present', 'mark_as_absent', 'mark_as_excused']
    
    @admin.action(description='Segna come PRESENTE')
    def mark_as_present(self, request, queryset):
        updated = queryset.update(status=Attendance.Status.PRESENT)
        self.message_user(request, f'{updated} presenze aggiornate a PRESENTE.')
    
    @admin.action(description='Segna come ASSENTE')
    def mark_as_absent(self, request, queryset):
        updated = queryset.update(status=Attendance.Status.ABSENT)
        self.message_user(request, f'{updated} presenze aggiornate a ASSENTE.')
    
    @admin.action(description='Segna come GIUSTIFICATO')
    def mark_as_excused(self, request, queryset):
        updated = queryset.update(status=Attendance.Status.EXCUSED)
        self.message_user(request, f'{updated} presenze aggiornate a GIUSTIFICATO.')
