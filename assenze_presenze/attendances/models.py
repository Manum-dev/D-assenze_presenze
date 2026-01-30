from django.db import models
from django.conf import settings

# Create your models here.
class Attendance(models.Model):
    """
    Modello per la gestione delle presenze/assenze.
    
    Ogni record rappresenta la presenza di un partecipante
    in una specifica giornata di corso.
    
    Stati possibili:
    - PRESENT: Presente
    - ABSENT: Assente
    - EXCUSED: Giustificato (conta come presenza per la percentuale)
    """
    
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Presente'
        ABSENT = 'ABSENT', 'Assente'
        EXCUSED = 'EXCUSED', 'Giustificato'
    
    # Relazione con l'utente (può essere null se non ancora registrato)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances',
        verbose_name='Utente',
        help_text='Collegato quando il partecipante si registra'
    )
    
    # Relazione con la giornata di corso
    course_day = models.ForeignKey(
        'course_days.CourseDay',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Giornata'
    )
    
    # Identificativo partecipante (email o codice)
    # Usato per registrare presenze prima che l'utente si registri
    participant_identifier = models.CharField(
        max_length=255,
        verbose_name='Identificativo partecipante',
        help_text='Email o codice identificativo'
    )
    
    # Stato presenza
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABSENT,
        verbose_name='Stato'
    )
    
    # Note aggiuntive
    notes = models.TextField(
        blank=True,
        verbose_name='Note',
        help_text='Es: certificato medico, ritardo, ecc.'
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
    
    class Meta:
        ordering = ['course_day__date', 'participant_identifier']
        verbose_name = 'Presenza'
        verbose_name_plural = 'Presenze'
        # Vincolo: un partecipante può avere UNA sola presenza per giornata
        unique_together = ['course_day', 'participant_identifier']
    
    def __str__(self):
        return f"{self.participant_identifier} - {self.course_day.date} - {self.get_status_display()}"
    
    def is_present(self):
        """Verifica se è presente (include giustificati)"""
        return self.status in [self.Status.PRESENT, self.Status.EXCUSED]