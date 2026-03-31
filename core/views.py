from django.shortcuts import render, redirect
from django.contrib import messages
from imoveis.models import Imovel
from leads.models import Lead
from leads.forms import ContatoForm


def home(request):
    imoveis = Imovel.objects.filter(
        ativo=True, status='disponivel'
    ).prefetch_related('fotos')

    destaques = imoveis.filter(destaque__in=['destaque', 'exclusivo'])
    imoveis = imoveis[:6]  # slice DEPOIS do filtro de destaques

    return render(request, 'core/home.html', {
        'imoveis': imoveis,
        'destaques': destaques,
    })


def sobre(request):
    return render(request, 'core/sobre.html')


def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem enviada! Retornarei em breve.')
            return redirect('core:contato')
    else:
        form = ContatoForm()
    return render(request, 'core/contato.html', {'form': form})