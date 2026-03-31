from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Rafael Moura Imóveis"
admin.site.site_title = "Painel Administrativo"
admin.site.index_title = "Gestão de Imóveis"

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
    path('imoveis/', include('imoveis.urls')),
    path('painel/', include('core.admin_urls')),
    path('leads/', include('leads.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
