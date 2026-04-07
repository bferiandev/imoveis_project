from core.models import LogAtividade


def registrar_log(request, acao, modelo, descricao, objeto_id=None):
    """Registra uma ação do usuário no log."""
    try:
        LogAtividade.objects.create(
            usuario=request.user,
            acao=acao,
            modelo=modelo,
            objeto_id=objeto_id,
            descricao=descricao,
        )
    except Exception:
        pass  # Log nunca deve quebrar o fluxo principal