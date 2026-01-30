from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permesso: solo utenti con ruolo ADMIN.
    Usato per proteggere gli endpoint di amministrazione.
    """
    message = "Accesso riservato agli amministratori."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsParticipant(BasePermission):
    """
    Permesso: solo utenti con ruolo PARTICIPANT.
    Usato per proteggere gli endpoint dei partecipanti.
    """
    message = "Accesso riservato ai partecipanti."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'PARTICIPANT'
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Permesso: admin può fare tutto, altri solo lettura.
    """
    message = "Modifica riservata agli amministratori."
    
    def has_permission(self, request, view):
        # Lettura permessa a tutti gli autenticati
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        # Scrittura solo admin
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )