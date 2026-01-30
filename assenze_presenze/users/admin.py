from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin panel per la gestione utenti"""
    
    # Colonne nella lista
    list_display = [
        'email',
        'username',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'created_at'
    ]
    
    # Filtri laterali
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    
    # Campi di ricerca
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    # Ordinamento default
    ordering = ['-created_at']
    
    # Campi nel form di modifica
    fieldsets = UserAdmin.fieldsets + (
        ('Informazioni Aggiuntive', {
            'fields': ('role', 'phone', 'birth_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Campi in sola lettura
    readonly_fields = ['created_at', 'updated_at']
    
    # Campi nel form di creazione
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informazioni Aggiuntive', {
            'fields': ('email', 'first_name', 'last_name', 'role', 'phone', 'birth_date')
        }),
    )
