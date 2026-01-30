from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Modello utente personalizzato.
    
    Ruoli:
    - ADMIN: può gestire tutto (primo utente registrato)
    - PARTICIPANT: può solo vedere le proprie presenze
    """
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Amministratore'
        PARTICIPANT = 'PARTICIPANT', 'Partecipante'
    
    # Campi personalizzati
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Utilizzato per il login'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARTICIPANT,
        verbose_name='Ruolo'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefono'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data di nascita'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data creazione'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ultimo aggiornamento'
    )
    
    # Usa email come username per il login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Utente'
        verbose_name_plural = 'Utenti'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Restituisce nome completo"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_admin(self):
        """Verifica se l'utente è admin"""
        return self.role == self.Role.ADMIN
    
    def is_participant(self):
        """Verifica se l'utente è partecipante"""
        return self.role == self.Role.PARTICIPANT
    
    def promote_to_admin(self):
        """Promuove l'utente ad admin"""
        self.role = self.Role.ADMIN
        self.save(update_fields=['role', 'updated_at'])
    
    def demote_to_participant(self):
        """Rimuove i privilegi admin"""
        self.role = self.Role.PARTICIPANT
        self.save(update_fields=['role', 'updated_at'])
