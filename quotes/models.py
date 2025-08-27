from django.db import models
from django.conf import settings

class QuoteRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='quote_requests'
    )

    # Collected inputs
    produit = models.CharField(max_length=32)
    age = models.PositiveIntegerField()
    capital = models.PositiveIntegerField()
    duree = models.PositiveIntegerField()
    fumeur = models.BooleanField()

    # Final computed/sourced quote
    devis = models.JSONField()
    source = models.CharField(max_length=20, default='simulated')  # 'api' or 'simulated'

    # Request context
    session_key = models.CharField(max_length=64, blank=True, default='')
    user_agent = models.TextField(blank=True, default='')
    ip_address = models.CharField(max_length=64, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        who = self.user.email if self.user else 'anonymous'
        return f"Quote({self.produit}, {self.capital} TND, {who}, {self.created_at:%Y-%m-%d})"

