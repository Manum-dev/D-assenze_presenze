from django.urls import path
from .views import (
    AdminDashboardView,
    AdminUserListCreateView,
    AdminUserDetailView,
    PromoteUserView,
    DemoteUserView,
    AdminListView,
    ParticipantListView,
)

urlpatterns = [
    # Dashboard
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Gestione utenti
    path('admin/users/', AdminUserListCreateView.as_view(), name='admin-users-list'),
    path('admin/users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    
    # Promozione/Rimozione admin
    path('admin/users/<int:user_id>/promote/', PromoteUserView.as_view(), name='promote-user'),
    path('admin/users/<int:user_id>/demote/', DemoteUserView.as_view(), name='demote-user'),
    
    # Liste filtrate
    path('admin/admins/', AdminListView.as_view(), name='admin-list'),
    path('admin/participants/', ParticipantListView.as_view(), name='participant-list'),
]