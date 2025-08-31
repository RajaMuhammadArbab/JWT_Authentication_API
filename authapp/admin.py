from django.contrib import admin
from .models import RefreshToken

@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'jti', 'revoked', 'created_at', 'expires_at', 'rotated_from')
    search_fields = ('user__username', 'jti')
