from django.db import models


class CourseDay(models.Model):
    """
    Rappresenta una singola giornata di corso.
    L'admin crea le giornate, poi associa presenze/assenze.
    """
    date = models.DateField(
        unique=True,
        verbose_name='Data'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Descrizione',
        help_text='Es: Lezione 1 - Introduzione a Django'
    )
    is_holiday = models.BooleanField(
        default=False,
        verbose_name='Giorno festivo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date']
        verbose_name = 'Giornata Corso'
        verbose_name_plural = 'Giornate Corso'
    
    def __str__(self):
        return f"{self.date} - {self.description or 'Lezione'}"
