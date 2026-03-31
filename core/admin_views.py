from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from imoveis.models import Imovel, FotoImovel
from imoveis.forms import ImovelForm, FotoImovelFormSet
from leads.models import Lead
import json


@login_required
def dashboard(request):
    total_imoveis = Imovel.objects.filter(ativo=True).count()
    imoveis_disponiveis = Imovel.objects.filter(status='disponivel', ativo=True).count()
    imoveis_vendidos = Imovel.objects.filter(status='vendido').count()
    total_leads = Lead.objects.count()
    leads_novos = Lead.objects.filter(status='novo').count()
    leads_recentes = Lead.objects.select_related('imovel').order_by('-criado_em')[:5]
    imoveis_recentes = Imovel.objects.prefetch_related('fotos').order_by('-criado_em')[:4]

    # Métricas por tipo
    por_tipo = list(
        Imovel.objects.filter(ativo=True)
        .values('tipo')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Leads por status
    leads_por_status = {
        item['status']: item['total']
        for item in Lead.objects.values('status').annotate(total=Count('id'))
    }

    return render(request, 'painel/dashboard.html', {
        'total_imoveis': total_imoveis,
        'imoveis_disponiveis': imoveis_disponiveis,
        'imoveis_vendidos': imoveis_vendidos,
        'total_leads': total_leads,
        'leads_novos': leads_novos,
        'leads_recentes': leads_recentes,
        'imoveis_recentes': imoveis_recentes,
        'por_tipo': por_tipo,
        'leads_por_status': leads_por_status,
    })


# ─── IMÓVEIS ──────────────────────────────────────────

@login_required
def imovel_list(request):
    qs = Imovel.objects.prefetch_related('fotos').select_related('cidade', 'bairro')
    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(cidade__nome__icontains=q))
    if tipo:
        qs = qs.filter(tipo=tipo)
    if status:
        qs = qs.filter(status=status)
    return render(request, 'painel/imovel_list.html', {
        'imoveis': qs,
        'q': q, 'tipo': tipo, 'status': status,
        'tipo_choices': Imovel.TIPO_CHOICES,
        'status_choices': Imovel.STATUS_CHOICES,
    })


@login_required
def imovel_create(request):
    if request.method == 'POST':
        form = ImovelForm(request.POST)
        if form.is_valid():
            imovel = form.save()
            # Salvar fotos enviadas
            fotos = request.FILES.getlist('fotos')
            for i, foto in enumerate(fotos):
                FotoImovel.objects.create(
                    imovel=imovel,
                    imagem=foto,
                    principal=(i == 0),
                    ordem=i
                )
            messages.success(request, f'Imóvel "{imovel.titulo}" criado com sucesso!')
            return redirect('painel:imovel_fotos', pk=imovel.pk)
    else:
        form = ImovelForm()
    return render(request, 'painel/imovel_form.html', {'form': form, 'titulo': 'Novo Imóvel'})


@login_required
def imovel_edit(request, pk):
    imovel = get_object_or_404(Imovel, pk=pk)
    if request.method == 'POST':
        form = ImovelForm(request.POST, instance=imovel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imóvel atualizado com sucesso!')
            return redirect('painel:imovel_list')
    else:
        form = ImovelForm(instance=imovel)
    return render(request, 'painel/imovel_form.html', {
        'form': form, 'imovel': imovel,
        'titulo': f'Editar: {imovel.titulo}'
    })


@login_required
@require_POST
def imovel_delete(request, pk):
    imovel = get_object_or_404(Imovel, pk=pk)
    nome = imovel.titulo
    imovel.delete()
    messages.success(request, f'Imóvel "{nome}" excluído.')
    return redirect('painel:imovel_list')


@login_required
def imovel_fotos(request, pk):
    imovel = get_object_or_404(Imovel, pk=pk)
    if request.method == 'POST':
        fotos = request.FILES.getlist('fotos')
        ultima_ordem = imovel.fotos.count()
        for i, foto in enumerate(fotos):
            FotoImovel.objects.create(
                imovel=imovel,
                imagem=foto,
                ordem=ultima_ordem + i,
                principal=(ultima_ordem == 0 and i == 0)
            )
        messages.success(request, f'{len(fotos)} foto(s) adicionada(s)!')
        return redirect('painel:imovel_fotos', pk=pk)
    return render(request, 'painel/imovel_fotos.html', {'imovel': imovel})


@login_required
@require_POST
def foto_delete(request, pk):
    foto = get_object_or_404(FotoImovel, pk=pk)
    imovel_pk = foto.imovel.pk
    foto.imagem.delete(save=False)
    foto.delete()
    messages.success(request, 'Foto removida.')
    return redirect('painel:imovel_fotos', pk=imovel_pk)


@login_required
@require_POST
def foto_set_principal(request, pk):
    foto = get_object_or_404(FotoImovel, pk=pk)
    FotoImovel.objects.filter(imovel=foto.imovel).update(principal=False)
    foto.principal = True
    foto.save()
    messages.success(request, 'Foto principal definida!')
    return redirect('painel:imovel_fotos', pk=foto.imovel.pk)


# ─── LEADS ────────────────────────────────────────────

@login_required
def lead_list(request):
    qs = Lead.objects.select_related('imovel')
    status = request.GET.get('status', '')
    q = request.GET.get('q', '')
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(telefone__icontains=q))
    return render(request, 'painel/lead_list.html', {
        'leads': qs,
        'status': status, 'q': q,
        'status_choices': Lead.STATUS_CHOICES,
        'leads_novos': Lead.objects.filter(status='novo').count(),
    })


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        lead.anotacoes = request.POST.get('anotacoes', '')
        lead.status = request.POST.get('status', lead.status)
        lead.save()
        messages.success(request, 'Lead atualizado!')
        return redirect('painel:lead_detail', pk=pk)
    return render(request, 'painel/lead_detail.html', {
        'lead': lead,
        'status_choices': Lead.STATUS_CHOICES,
    })


@login_required
@require_POST
def lead_status(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    data = json.loads(request.body)
    lead.status = data.get('status', lead.status)
    lead.save()
    return JsonResponse({'ok': True})
