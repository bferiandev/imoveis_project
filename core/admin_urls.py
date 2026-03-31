from django.urls import path
from . import admin_views

app_name = 'painel'

urlpatterns = [
    path('', admin_views.dashboard, name='dashboard'),

    # Imóveis
    path('imoveis/', admin_views.imovel_list, name='imovel_list'),
    path('imoveis/novo/', admin_views.imovel_create, name='imovel_create'),
    path('imoveis/<int:pk>/editar/', admin_views.imovel_edit, name='imovel_edit'),
    path('imoveis/<int:pk>/excluir/', admin_views.imovel_delete, name='imovel_delete'),
    path('imoveis/<int:pk>/fotos/', admin_views.imovel_fotos, name='imovel_fotos'),
    path('fotos/<int:pk>/excluir/', admin_views.foto_delete, name='foto_delete'),
    path('fotos/<int:pk>/principal/', admin_views.foto_set_principal, name='foto_principal'),

    # Leads
    path('leads/', admin_views.lead_list, name='lead_list'),
    path('leads/<int:pk>/', admin_views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/status/', admin_views.lead_status, name='lead_status'),
]
