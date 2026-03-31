from django.shortcuts import redirect
from django.contrib import messages
from .forms import ContatoForm


def contato_imovel(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem enviada!')
    return redirect('core:home')
