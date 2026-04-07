"""
Motor de roteamento de leads.
Desativado por padrão — ative em settings.py:
DISTRIBUICAO_LEADS_ATIVA = True
"""
from django.conf import settings
from django.db.models import F


def rotear_lead(lead):
    """
    Analisa o lead e atribui ao corretor correto.
    Retorna o corretor atribuído ou None.
    """
    if not getattr(settings, 'DISTRIBUICAO_LEADS_ATIVA', False):
        return None

    from core.models import RegraRoteamento, PerfilCorretor

    # Encontra a primeira regra que bate com o lead
    time = _encontrar_time(lead)
    if not time:
        return None

    # Pega o próximo corretor da fila nesse time (round-robin)
    corretor_perfil = _proximo_corretor(time)
    if not corretor_perfil:
        return None

    # Atribui o lead
    lead.corretor = corretor_perfil.user
    lead.distribuido_automaticamente = True
    lead.save(update_fields=['corretor', 'distribuido_automaticamente'])

    # Incrementa contador e avança fila
    PerfilCorretor.objects.filter(pk=corretor_perfil.pk).update(
        total_leads_recebidos=F('total_leads_recebidos') + 1,
        posicao_fila=F('posicao_fila') + 1
    )

    return corretor_perfil.user


def _encontrar_time(lead):
    """Avalia as regras em ordem de prioridade."""
    from core.models import RegraRoteamento

    regras = RegraRoteamento.objects.filter(ativa=True).select_related('time')

    for regra in regras:
        if not regra.time.ativo:
            continue
        if regra.operacao and regra.operacao != lead.operacao:
            continue
        if regra.tipo_imovel and regra.tipo_imovel != lead.tipo_imovel:
            continue
        if regra.perfil_cliente and regra.perfil_cliente != lead.perfil_cliente:
            continue
        if regra.ticket_min and lead.ticket_estimado:
            if lead.ticket_estimado < regra.ticket_min:
                continue
        if regra.ticket_max and lead.ticket_estimado:
            if lead.ticket_estimado > regra.ticket_max:
                continue
        if regra.regiao and regra.regiao.lower() not in lead.regiao.lower():
            continue
        return regra.time

    return None


def _proximo_corretor(time):
    """Round-robin — pega o corretor com menor posição na fila."""
    return (
        time.corretores
        .filter(ativo=True)
        .order_by('posicao_fila', 'total_leads_recebidos')
        .first()
    )