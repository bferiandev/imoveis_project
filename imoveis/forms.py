from django import forms
from django.forms import inlineformset_factory
from .models import Imovel, FotoImovel


class ImovelForm(forms.ModelForm):
    class Meta:
        model = Imovel
        exclude = ['slug', 'visualizacoes', 'criado_em', 'atualizado_em']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex: Cobertura Duplex com Vista para a Cidade'}),
            'descricao': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Descreva o imóvel com detalhes...'}),
            'diferenciais': forms.Textarea(attrs={'rows': 6,
                'placeholder': 'Piscina privativa\nAutomação residencial\nVista panorâmica\n...'}),
            'meta_descricao': forms.TextInput(attrs={'placeholder': 'Resumo para Google (até 160 caracteres)'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, número, complemento'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control')
            else:
                field.widget.attrs.setdefault('class', 'form-check-input')


FotoImovelFormSet = inlineformset_factory(
    Imovel, FotoImovel,
    fields=['imagem', 'legenda', 'principal', 'ordem'],
    extra=3,
    can_delete=True,
)
