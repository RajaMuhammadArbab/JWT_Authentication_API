from django.db import models
from django.conf import settings
from django.utils import timezone

class RefreshToken(models.Model):
   
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='refresh_tokens'
    )
    jti = models.CharField(max_length=255, unique=True)
    token_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    rotated_from = models.CharField(max_length=255, null=True, blank=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"RefreshToken(user={self.user}, jti={self.jti}, revoked={self.revoked})"
