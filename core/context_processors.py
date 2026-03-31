from django.conf import settings


def site_settings(request):
    return {
        'WHATSAPP_NUMBER': getattr(settings, 'WHATSAPP_NUMBER', '5511999999999'),
        'BROKER_NAME': getattr(settings, 'BROKER_NAME', 'Rafael Moura'),
        'BROKER_CRECI': getattr(settings, 'BROKER_CRECI', '123456-F'),
    }
