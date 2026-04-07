from django.contrib import admin
from .models import Imovel, FotoImovel, Cidade, Bairro


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'estado']
    ordering = ['nome']


@admin.register(Bairro)
class BairroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cidade']
    list_filter = ['cidade']
    ordering = ['nome']


class FotoInline(admin.TabularInline):
    model = FotoImovel
    extra = 3


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'status', 'preco', 'cidade', 'ativo']
    list_filter = ['tipo', 'status', 'cidade', 'ativo']
    search_fields = ['titulo', 'descricao']
    prepopulated_fields = {'slug': ('titulo',)}
    inlines = [FotoInline]