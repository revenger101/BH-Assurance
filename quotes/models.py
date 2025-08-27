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

    # Basic info
    produit = models.CharField(max_length=32)

    # Store all collected inputs as JSON (flexible for different products)
    collected_data = models.JSONField(default=dict)

    # Legacy fields (kept for backward compatibility)
    age = models.PositiveIntegerField(null=True, blank=True)
    capital = models.PositiveIntegerField(null=True, blank=True)
    duree = models.PositiveIntegerField(null=True, blank=True)
    fumeur = models.BooleanField(null=True, blank=True)

    # Quote result
    devis = models.JSONField()
    source = models.CharField(max_length=30, default='simulated')  # 'api_externe', 'simulated', 'api'

    # Request context
    session_key = models.CharField(max_length=64, blank=True, default='')
    user_agent = models.TextField(blank=True, default='')
    ip_address = models.CharField(max_length=64, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        who = self.user.email if self.user else 'anonymous'
        capital_info = self.collected_data.get('capital') or self.collected_data.get('valeur_venale') or 'N/A'
        return f"Quote({self.produit}, {capital_info} TND, {who}, {self.created_at:%Y-%m-%d})"

