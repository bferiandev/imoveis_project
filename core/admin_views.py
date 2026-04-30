from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from core.models import PerfilCorretor, Time, RegraRoteamento, LogAtividade
from core.decorators import admin_required, corretor_required
from core.utils import registrar_log
from imoveis.models import Imovel, FotoImovel
from imoveis.forms import ImovelForm, FotoImovelFormSet
from imoveis.models import Proprietario
from leads.models import Lead
from imoveis.models import Cidade, Bairro
from imoveis.models import Imovel, FotoImovel, DocumentoImovel
import os
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
        qs = qs.filter(
            Q(titulo__icontains=q) |
            Q(cidade__nome__icontains=q) |
            Q(codigo__icontains=q)
        )
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
            registrar_log(request, 'criar', 'Imóvel',
                        f'Criou o imóvel "{imovel.titulo}"', imovel.pk)
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
            registrar_log(request, 'editar', 'Imóvel',
                         f'Editou o imóvel "{imovel.titulo}"', imovel.pk)
            messages.success(request, 'Imóvel atualizado com sucesso!')
            return redirect('painel:imovel_list')
    else:
        form = ImovelForm(instance=imovel)
    return render(request, 'painel/imovel_form.html', {
        'form': form, 'imovel': imovel,
        'titulo': f'Editar: {imovel.titulo}'
    })


@admin_required
@require_POST
def imovel_delete(request, pk):
    imovel = get_object_or_404(Imovel, pk=pk)
    nome = imovel.titulo
    imovel.delete()
    registrar_log(request, 'excluir', 'Imóvel', f'Excluiu o imóvel "{nome}"')
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
        registrar_log(request, 'foto', 'Imóvel',
                     f'Adicionou {len(fotos)} foto(s) em "{imovel.titulo}"', imovel.pk)
        messages.success(request, f'{len(fotos)} foto(s) adicionada(s)!')
        return redirect('painel:imovel_fotos', pk=pk)
    return render(request, 'painel/imovel_fotos.html', {'imovel': imovel})


@admin_required
@require_POST
def foto_delete(request, pk):
    foto = get_object_or_404(FotoImovel, pk=pk)
    imovel_pk = foto.imovel.pk
    foto.imagem.delete(save=False)
    foto.delete()
    messages.success(request, 'Foto removida.')
    return redirect('painel:imovel_fotos', pk=imovel_pk)


@admin_required
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
    registrar_log(request, 'status', 'Lead',
                 f'Alterou status do lead "{lead.nome}" de {status_anterior} para {lead.status}',
                 lead.pk)
    return JsonResponse({'ok': True})



# ─── CIDADES ──────────────────────────────────────────

@login_required
def cidade_list(request):
    cidades = Cidade.objects.annotate(total_bairros=Count('bairros')).order_by('nome')
    return render(request, 'painel/cidade_list.html', {'cidades': cidades})


@admin_required
def cidade_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        estado = request.POST.get('estado', 'SP').strip()
        if nome:
            Cidade.objects.create(nome=nome, estado=estado)
            messages.success(request, f'Cidade "{nome}" criada!')
            return redirect('painel:cidade_list')
    return render(request, 'painel/cidade_form.html', {'titulo': 'Nova Cidade'})


@admin_required
def cidade_edit(request, pk):
    cidade = get_object_or_404(Cidade, pk=pk)
    if request.method == 'POST':
        cidade.nome = request.POST.get('nome', cidade.nome).strip()
        cidade.estado = request.POST.get('estado', cidade.estado).strip()
        cidade.save()
        messages.success(request, 'Cidade atualizada!')
        return redirect('painel:cidade_list')
    return render(request, 'painel/cidade_form.html', {'titulo': 'Editar Cidade', 'cidade': cidade})


@admin_required
@require_POST
def cidade_delete(request, pk):
    cidade = get_object_or_404(Cidade, pk=pk)
    nome = cidade.nome
    cidade.delete()
    messages.success(request, f'Cidade "{nome}" excluída.')
    return redirect('painel:cidade_list')


# ─── BAIRROS ──────────────────────────────────────────

@login_required
def bairro_list(request):
    bairros = Bairro.objects.select_related('cidade').order_by('cidade__nome', 'nome')
    return render(request, 'painel/bairro_list.html', {'bairros': bairros})


@admin_required
def bairro_create(request):
    cidades = Cidade.objects.order_by('nome')
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        cidade_id = request.POST.get('cidade')
        if nome and cidade_id:
            Bairro.objects.create(nome=nome, cidade_id=cidade_id)
            messages.success(request, f'Bairro "{nome}" criado!')
            return redirect('painel:bairro_list')
    return render(request, 'painel/bairro_form.html', {'titulo': 'Novo Bairro', 'cidades': cidades})


@admin_required
def bairro_edit(request, pk):
    bairro = get_object_or_404(Bairro, pk=pk)
    cidades = Cidade.objects.order_by('nome')
    if request.method == 'POST':
        bairro.nome = request.POST.get('nome', bairro.nome).strip()
        bairro.cidade_id = request.POST.get('cidade', bairro.cidade_id)
        bairro.save()
        messages.success(request, 'Bairro atualizado!')
        return redirect('painel:bairro_list')
    return render(request, 'painel/bairro_form.html', {
        'titulo': 'Editar Bairro', 'bairro': bairro, 'cidades': cidades
    })


@admin_required
@require_POST
def bairro_delete(request, pk):
    bairro = get_object_or_404(Bairro, pk=pk)
    nome = bairro.nome
    bairro.delete()
    messages.success(request, f'Bairro "{nome}" excluído.')
    return redirect('painel:bairro_list')


# ─── PROPRIETÁRIOS ────────────────────────────────────

@login_required
def proprietario_list(request):
    q = request.GET.get('q', '')
    qs = Proprietario.objects.annotate(total_imoveis=Count('imoveis'))
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(telefone__icontains=q))
    return render(request, 'painel/proprietario_list.html', {'proprietarios': qs, 'q': q})


@login_required
def proprietario_create(request):
    if request.method == 'POST':
        p = Proprietario()
        p.nome = request.POST.get('nome', '').strip()
        p.tipo = request.POST.get('tipo', 'pf')
        p.cpf_cnpj = request.POST.get('cpf_cnpj', '').strip()
        p.telefone = request.POST.get('telefone', '').strip()
        p.telefone2 = request.POST.get('telefone2', '').strip()
        p.email = request.POST.get('email', '').strip()
        p.observacoes = request.POST.get('observacoes', '').strip()
        if p.nome and p.telefone:
            p.save()
            registrar_log(request, 'criar', 'Proprietário',
                         f'Criou o proprietário "{p.nome}"', p.pk)
            messages.success(request, f'Proprietário "{p.nome}" criado!')
            return redirect('painel:proprietario_list')
        messages.error(request, 'Nome e telefone são obrigatórios.')
    return render(request, 'painel/proprietario_form.html', {'titulo': 'Novo Proprietário'})


@admin_required
def proprietario_edit(request, pk):
    p = get_object_or_404(Proprietario, pk=pk)
    if request.method == 'POST':
        p.nome = request.POST.get('nome', p.nome).strip()
        p.tipo = request.POST.get('tipo', p.tipo)
        p.cpf_cnpj = request.POST.get('cpf_cnpj', p.cpf_cnpj).strip()
        p.telefone = request.POST.get('telefone', p.telefone).strip()
        p.telefone2 = request.POST.get('telefone2', p.telefone2).strip()
        p.email = request.POST.get('email', p.email).strip()
        p.observacoes = request.POST.get('observacoes', p.observacoes).strip()
        p.save()
        messages.success(request, 'Proprietário atualizado!')
        return redirect('painel:proprietario_detail', pk=pk)
    return render(request, 'painel/proprietario_form.html', {
        'titulo': f'Editar: {p.nome}', 'proprietario': p
    })


@login_required
def proprietario_detail(request, pk):
    p = get_object_or_404(Proprietario, pk=pk)
    imoveis = p.imoveis.prefetch_related('fotos').all()
    return render(request, 'painel/proprietario_detail.html', {
        'proprietario': p, 'imoveis': imoveis
    })


@admin_required
@require_POST
def proprietario_delete(request, pk):
    p = get_object_or_404(Proprietario, pk=pk)
    nome = p.nome
    p.delete()
    messages.success(request, f'Proprietário "{nome}" excluído.')
    return redirect('painel:proprietario_list')


# ─── TIMES ────────────────────────────────────────────

@admin_required
def time_list(request):
    times = Time.objects.annotate(
        total_corretores=Count('corretores'),
        total_regras=Count('regras')
    )
    return render(request, 'painel/time_list.html', {'times': times})


@admin_required
def time_create(request):
    if request.method == 'POST':
        t = Time()
        t.nome = request.POST.get('nome', '').strip()
        t.tipo = request.POST.get('tipo', '').strip()
        t.descricao = request.POST.get('descricao', '').strip()
        t.cor = request.POST.get('cor', '#b8974a').strip()
        t.ativo = request.POST.get('ativo') == 'on'
        if t.nome and t.tipo:
            t.save()
            messages.success(request, f'Time "{t.nome}" criado!')
            return redirect('painel:time_list')
        messages.error(request, 'Nome e tipo são obrigatórios.')
    return render(request, 'painel/time_form.html', {'titulo': 'Novo Time'})


@admin_required
def time_edit(request, pk):
    t = get_object_or_404(Time, pk=pk)
    if request.method == 'POST':
        t.nome = request.POST.get('nome', t.nome).strip()
        t.descricao = request.POST.get('descricao', t.descricao).strip()
        t.cor = request.POST.get('cor', t.cor).strip()
        t.ativo = request.POST.get('ativo') == 'on'
        t.save()
        messages.success(request, 'Time atualizado!')
        return redirect('painel:time_list')
    return render(request, 'painel/time_form.html', {
        'titulo': f'Editar: {t.nome}', 'time': t
    })


# ─── REGRAS DE ROTEAMENTO ─────────────────────────────

@admin_required
def regra_list(request):
    regras = RegraRoteamento.objects.select_related('time').order_by('prioridade')
    times = Time.objects.filter(ativo=True)
    return render(request, 'painel/regra_list.html', {
        'regras': regras, 'times': times
    })


@admin_required
def regra_create(request):
    times = Time.objects.filter(ativo=True)
    if request.method == 'POST':
        r = RegraRoteamento()
        r.nome = request.POST.get('nome', '').strip()
        r.time_id = request.POST.get('time')
        r.prioridade = request.POST.get('prioridade', 0)
        r.operacao = request.POST.get('operacao', '')
        r.tipo_imovel = request.POST.get('tipo_imovel', '')
        r.perfil_cliente = request.POST.get('perfil_cliente', '')
        r.regiao = request.POST.get('regiao', '').strip()
        r.ativa = request.POST.get('ativa') == 'on'
        ticket_min = request.POST.get('ticket_min', '').strip()
        ticket_max = request.POST.get('ticket_max', '').strip()
        r.ticket_min = ticket_min if ticket_min else None
        r.ticket_max = ticket_max if ticket_max else None
        if r.nome and r.time_id:
            r.save()
            messages.success(request, f'Regra "{r.nome}" criada!')
            return redirect('painel:regra_list')
        messages.error(request, 'Nome e time são obrigatórios.')
    return render(request, 'painel/regra_form.html', {
        'titulo': 'Nova Regra', 'times': times
    })


@admin_required
def regra_edit(request, pk):
    r = get_object_or_404(RegraRoteamento, pk=pk)
    times = Time.objects.filter(ativo=True)
    if request.method == 'POST':
        r.nome = request.POST.get('nome', r.nome).strip()
        r.time_id = request.POST.get('time', r.time_id)
        r.prioridade = request.POST.get('prioridade', r.prioridade)
        r.operacao = request.POST.get('operacao', '')
        r.tipo_imovel = request.POST.get('tipo_imovel', '')
        r.perfil_cliente = request.POST.get('perfil_cliente', '')
        r.regiao = request.POST.get('regiao', '').strip()
        r.ativa = request.POST.get('ativa') == 'on'
        ticket_min = request.POST.get('ticket_min', '').strip()
        ticket_max = request.POST.get('ticket_max', '').strip()
        r.ticket_min = ticket_min if ticket_min else None
        r.ticket_max = ticket_max if ticket_max else None
        r.save()
        messages.success(request, 'Regra atualizada!')
        return redirect('painel:regra_list')
    return render(request, 'painel/regra_form.html', {
        'titulo': f'Editar: {r.nome}', 'regra': r, 'times': times
    })


@admin_required
def regra_delete(request, pk):
    r = get_object_or_404(RegraRoteamento, pk=pk)
    nome = r.nome
    r.delete()
    messages.success(request, f'Regra "{nome}" excluída.')
    return redirect('painel:regra_list')






# ─── USUÁRIOS / CORRETORES ────────────────────────────

@admin_required
def usuario_list(request):
    usuarios = User.objects.select_related('perfil').order_by('first_name')
    return render(request, 'painel/usuario_list.html', {'usuarios': usuarios})


@admin_required
def usuario_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        is_staff = request.POST.get('is_staff') == 'on'
        creci = request.POST.get('creci', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        bio = request.POST.get('bio', '').strip()
        ativo = request.POST.get('ativo') == 'on'
        time_id = request.POST.get('time') or None

        if not username or not password:
            messages.error(request, 'Usuário e senha são obrigatórios.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Este usuário já existe.')
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name, is_staff=is_staff
            )
            perfil, _ = PerfilCorretor.objects.get_or_create(user=user)
            perfil.creci = creci
            perfil.telefone = telefone
            perfil.bio = bio
            perfil.ativo = ativo
            perfil.time_id = time_id
            perfil.save()
            registrar_log(request, 'criar', 'Usuário',
                         f'Criou o usuário "{user.get_full_name() or username}"', user.pk)
            messages.success(request, f'Usuário "{first_name or username}" criado!')
            return redirect('painel:usuario_list')

    times = Time.objects.filter(ativo=True)
    return render(request, 'painel/usuario_form_create.html', {
        'titulo': 'Novo Usuário', 'times': times
    })


@admin_required
def usuario_edit(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    perfil, _ = PerfilCorretor.objects.get_or_create(user=usuario)
    times = Time.objects.filter(ativo=True)

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name', '').strip()
        usuario.last_name = request.POST.get('last_name', '').strip()
        usuario.email = request.POST.get('email', '').strip()
        usuario.is_staff = request.POST.get('is_staff') == 'on'
        nova_senha = request.POST.get('password', '').strip()
        if nova_senha:
            usuario.set_password(nova_senha)
        usuario.save()

        perfil.creci = request.POST.get('creci', '').strip()
        perfil.telefone = request.POST.get('telefone', '').strip()
        perfil.bio = request.POST.get('bio', '').strip()
        perfil.ativo = request.POST.get('ativo') == 'on'
        perfil.time_id = request.POST.get('time') or None
        perfil.save()

        registrar_log(request, 'editar', 'Usuário',
                     f'Editou o usuário "{usuario.get_full_name() or usuario.username}"', usuario.pk)
        messages.success(request, 'Usuário atualizado!')
        return redirect('painel:usuario_list')

    return render(request, 'painel/usuario_form_create.html', {
        'titulo': f'Editar: {usuario.get_full_name() or usuario.username}',
        'usuario': usuario, 'perfil': perfil, 'times': times
    })


@admin_required
def usuario_delete(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'Você não pode excluir seu próprio usuário.')
        return redirect('painel:usuario_list')
    nome = usuario.get_full_name() or usuario.username
    usuario.delete()
    registrar_log(request, 'excluir', 'Usuário', f'Excluiu o usuário "{nome}"')
    messages.success(request, f'Usuário "{nome}" excluído.')
    return redirect('painel:usuario_list')


# ─── LOG DE ATIVIDADES ────────────────────────────────

@admin_required
def log_list(request):
    logs = LogAtividade.objects.select_related('usuario').order_by('-criado_em')[:200]
    return render(request, 'painel/log_list.html', {'logs': logs})


# ─── DOCUMENTOS DOS IMÓVEIS ────────────────────────────────

@login_required
def imovel_documentos(request, pk):
    imovel = get_object_or_404(Imovel, pk=pk)
    documentos = imovel.documentos.select_related('enviado_por').all()

    if request.method == 'POST':
        arquivos = request.FILES.getlist('arquivos')
        tipo = request.POST.get('tipo', 'outro')
        observacao = request.POST.get('observacao', '').strip()
        nome_base = request.POST.get('nome', '').strip()

        for arquivo in arquivos:
            nome_display = nome_base or arquivo.name

            # Garante extensão correta baseada no content-type
            import mimetypes
            nome_arquivo = arquivo.name
            if '.' not in os.path.basename(nome_arquivo):
                ext = mimetypes.guess_extension(arquivo.content_type)
                if ext:
                    ext = ext.replace('.jpeg', '.jpg').replace('.jpe', '.jpg')
                    # Renomeia o arquivo internamente
                    arquivo.name = f"{nome_arquivo}{ext}"

            DocumentoImovel.objects.create(
                imovel=imovel,
                tipo=tipo,
                nome=nome_display,
                arquivo=arquivo,
                observacao=observacao,
                enviado_por=request.user
            )

        registrar_log(request, 'editar', 'Documento',
                     f'Adicionou {len(arquivos)} documento(s) em "{imovel.titulo}"', imovel.pk)
        messages.success(request, f'{len(arquivos)} documento(s) adicionado(s)!')
        return redirect('painel:imovel_documentos', pk=pk)

    return render(request, 'painel/imovel_documentos.html', {
        'imovel': imovel,
        'documentos': documentos,
        'tipo_choices': DocumentoImovel.TIPO_CHOICES,
    })


@login_required
@require_POST
def documento_delete(request, pk):
    doc = get_object_or_404(DocumentoImovel, pk=pk)
    imovel_pk = doc.imovel.pk
    doc.arquivo.delete(save=False)
    doc.delete()
    messages.success(request, 'Documento removido.')
    return redirect('painel:imovel_documentos', pk=imovel_pk)


@login_required
def documento_download(request, pk):
    from django.http import HttpResponseRedirect
    doc = get_object_or_404(DocumentoImovel, pk=pk)
    
    # Pega a URL base do Cloudinary e adiciona fl_attachment para forçar download com nome correto
    url = doc.arquivo.url
    nome = doc.nome or 'documento'
    
    # Detecta extensão pela URL ou content-type
    import mimetypes
    ext = ''
    if '.' in os.path.basename(doc.arquivo.name):
        ext = '.' + doc.arquivo.name.rsplit('.', 1)[-1]
    else:
        # Busca o content-type real do arquivo no Cloudinary
        import urllib.request
        with urllib.request.urlopen(url) as resp:
            ct = resp.headers.get('Content-Type', '').split(';')[0]
            ext = mimetypes.guess_extension(ct) or ''
            ext = ext.replace('.jpeg', '.jpg').replace('.jpe', '.jpg')
    
    filename = f"{nome}{ext}"
    
    # Adiciona fl_attachment na URL do Cloudinary para forçar download
    # Transforma: /image/upload/v1/... → /image/upload/fl_attachment:nome/v1/...
    if 'cloudinary.com' in url:
        url = url.replace('/upload/', f'/upload/fl_attachment:{filename}/')
    
    return HttpResponseRedirect(url)