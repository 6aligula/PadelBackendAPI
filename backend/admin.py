from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from backend.models import User, Reservation, Installation

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Añadimos los campos personalizados al panel
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('direccion', 'telefono')}),
    )
    list_display = ('username', 'email', 'direccion', 'telefono', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'direccion', 'telefono')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'installation_id', 'is_synced', 'created_at')  # Campos visibles en la lista
    list_filter = ('is_synced', 'date')  # Filtros laterales para búsqueda rápida
    search_fields = ('user__username', 'date', 'installation_id')  # Campos para la barra de búsqueda

@admin.register(Installation)
class InstallationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'capacity', 'roofed', 'area')
