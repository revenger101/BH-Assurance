from django.contrib import admin
from .models import QuoteRequest

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id','user','produit','capital','age','duree','fumeur','source','created_at'
    )
    list_filter = ('produit','fumeur','source','created_at')
    search_fields = ('user__email','produit','session_key','ip_address')
    readonly_fields = ('created_at','updated_at')

