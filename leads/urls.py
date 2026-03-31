from django.urls import path
from leads import views as lead_views

app_name = 'leads'

urlpatterns = [
    path('contato/', lead_views.contato_imovel, name='contato_imovel'),
]
