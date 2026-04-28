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

    # Proprietários
    path('proprietarios/', admin_views.proprietario_list, name='proprietario_list'),
    path('proprietarios/novo/', admin_views.proprietario_create, name='proprietario_create'),
    path('proprietarios/<int:pk>/editar/', admin_views.proprietario_edit, name='proprietario_edit'),
    path('proprietarios/<int:pk>/excluir/', admin_views.proprietario_delete, name='proprietario_delete'),
    path('proprietarios/<int:pk>/', admin_views.proprietario_detail, name='proprietario_detail'),

    # Leads
    path('leads/', admin_views.lead_list, name='lead_list'),
    path('leads/<int:pk>/', admin_views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/status/', admin_views.lead_status, name='lead_status'),

    # Times
    path('times/', admin_views.time_list, name='time_list'),
    path('times/novo/', admin_views.time_create, name='time_create'),
    path('times/<int:pk>/editar/', admin_views.time_edit, name='time_edit'),

    # Regras de Roteamento
    path('regras/', admin_views.regra_list, name='regra_list'),
    path('regras/nova/', admin_views.regra_create, name='regra_create'),
    path('regras/<int:pk>/editar/', admin_views.regra_edit, name='regra_edit'),
    path('regras/<int:pk>/excluir/', admin_views.regra_delete, name='regra_delete'),

    # Cidades
    path('cidades/', admin_views.cidade_list, name='cidade_list'),
    path('cidades/nova/', admin_views.cidade_create, name='cidade_create'),
    path('cidades/<int:pk>/editar/', admin_views.cidade_edit, name='cidade_edit'),
    path('cidades/<int:pk>/excluir/', admin_views.cidade_delete, name='cidade_delete'),

    # Bairros
    path('bairros/', admin_views.bairro_list, name='bairro_list'),
    path('bairros/novo/', admin_views.bairro_create, name='bairro_create'),
    path('bairros/<int:pk>/editar/', admin_views.bairro_edit, name='bairro_edit'),
    path('bairros/<int:pk>/excluir/', admin_views.bairro_delete, name='bairro_delete'),

    # Usuários
    path('usuarios/', admin_views.usuario_list, name='usuario_list'),
    path('usuarios/novo/', admin_views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', admin_views.usuario_edit, name='usuario_edit'),
    path('usuarios/<int:pk>/excluir/', admin_views.usuario_delete, name='usuario_delete'),

    # Documentos
    path('imoveis/<int:pk>/documentos/', admin_views.imovel_documentos, name='imovel_documentos'),
    path('documentos/<int:pk>/excluir/', admin_views.documento_delete, name='documento_delete'),
    path('documentos/<int:pk>/download/', admin_views.documento_download, name='documento_download'),

    # Registros de Atividades (Logs)
    path('atividades/', admin_views.log_list, name='log_list'),
]