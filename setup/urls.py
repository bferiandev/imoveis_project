from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import render

handler403 = lambda request, exception: render(request, 'painel/403.html', status=403)

admin.site.site_header = "Ferian e Tavares"
admin.site.site_title = "Painel Administrativo"
admin.site.index_title = "Gestão de Imóveis"

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
    path('imoveis/', include('imoveis.urls')),
    path('painel/', include('core.admin_urls')),
    path('painel/login/', auth_views.LoginView.as_view(), name='login'),
    path('painel/logout/', auth_views.LogoutView.as_view(next_page='/painel/login/'), name='logout'),
    path('leads/', include('leads.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
