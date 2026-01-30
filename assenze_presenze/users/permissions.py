from rest_framework.permissions import BasePermission


class IsParticipant(BasePermission):
    """
    Permette l'accesso solo agli utenti partecipanti
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_participant", False)
        )
