from django import forms
from .models import Lead


class ContatoForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['nome', 'telefone', 'email', 'interesse', 'mensagem', 'imovel']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Seu nome completo'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(11) 99999-9999'}),
            'email': forms.EmailInput(attrs={'placeholder': 'seu@email.com'}),
            'mensagem': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Como posso ajudar?'}),
        }
