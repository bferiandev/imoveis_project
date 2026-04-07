from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'operacao', 'status', 'criado_em']
    list_filter = ['status', 'operacao']
    search_fields = ['nome', 'telefone']