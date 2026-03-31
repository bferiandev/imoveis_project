from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Imovel, Cidade


def lista(request):
    qs = Imovel.objects.filter(ativo=True).prefetch_related('fotos').select_related('cidade', 'bairro')

    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    cidade = request.GET.get('cidade', '')
    preco_min = request.GET.get('preco_min', '')
    preco_max = request.GET.get('preco_max', '')
    ordem = request.GET.get('ordem', '-criado_em')

    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descricao__icontains=q) | Q(bairro__nome__icontains=q))
    if tipo:
        qs = qs.filter(tipo=tipo)
    if cidade:
        qs = qs.filter(cidade__id=cidade)
    if preco_min:
        qs = qs.filter(preco__gte=preco_min)
    if preco_max:
        qs = qs.filter(preco__lte=preco_max)
    if ordem in ['-criado_em', 'preco', '-preco']:
        qs = qs.order_by(ordem)

    cidades = Cidade.objects.all()
    return render(request, 'imoveis/lista.html', {
        'imoveis': qs,
        'cidades': cidades,
        'tipo_choices': Imovel.TIPO_CHOICES,
        'q': q, 'tipo': tipo, 'cidade': cidade,
        'preco_min': preco_min, 'preco_max': preco_max, 'ordem': ordem,
    })


def detalhe(request, slug):
    imovel = get_object_or_404(Imovel, slug=slug, ativo=True)
    # Incrementar visualizações
    Imovel.objects.filter(pk=imovel.pk).update(visualizacoes=imovel.visualizacoes + 1)
    relacionados = Imovel.objects.filter(
        tipo=imovel.tipo, ativo=True, status='disponivel'
    ).exclude(pk=imovel.pk).prefetch_related('fotos')[:3]
    return render(request, 'imoveis/detalhe.html', {
        'imovel': imovel,
        'relacionados': relacionados,
    })
