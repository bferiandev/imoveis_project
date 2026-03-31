from django.db import models
from imoveis.models import Imovel


class Lead(models.Model):
    INTERESSE_CHOICES = [
        ('comprar', 'Comprar imóvel'),
        ('vender', 'Vender imóvel'),
        ('investir', 'Investir'),
        ('visita', 'Agendar visita'),
        ('outro', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('em_contato', 'Em contato'),
        ('negociando', 'Negociando'),
        ('convertido', 'Convertido'),
        ('perdido', 'Perdido'),
    ]

    nome = models.CharField('Nome', max_length=150)
    telefone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('E-mail', blank=True)
    interesse = models.CharField('Interesse', max_length=20, choices=INTERESSE_CHOICES, default='comprar')
    mensagem = models.TextField('Mensagem', blank=True)
    imovel = models.ForeignKey(Imovel, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Imóvel de interesse', related_name='leads')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='novo')
    anotacoes = models.TextField('Anotações internas', blank=True)
    criado_em = models.DateTimeField('Recebido em', auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} — {self.get_interesse_display()}'

    @property
    def whatsapp_link(self):
        numero = self.telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not numero.startswith('55'):
            numero = '55' + numero
        return f'https://wa.me/{numero}'
