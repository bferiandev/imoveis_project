from django.conf import settings


def site_settings(request):
    return {
        'WHATSAPP_NUMBER': getattr(settings, 'WHATSAPP_NUMBER', '5511947532081'),
        'BROKER_NAME': getattr(settings, 'BROKER_NAME', 'Luiz Tavares'),
        'BROKER_CRECI': getattr(settings, 'BROKER_CRECI', '226905-F'),
        'DISTRIBUICAO_ATIVA': getattr(settings, 'DISTRIBUICAO_LEADS_ATIVA', False),
    }