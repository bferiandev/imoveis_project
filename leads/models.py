from django.db import models
from django.contrib.auth.models import User
from imoveis.models import Imovel


class Lead(models.Model):
    OPERACAO_CHOICES = [
        ('venda', 'Comprar imóvel'),
        ('locacao', 'Alugar imóvel'),
        ('lancamento', 'Lançamento'),
        ('investir', 'Investir'),
        ('vender', 'Vender meu imóvel'),
        ('outro', 'Outro'),
    ]
    TIPO_IMOVEL_CHOICES = [
        ('', 'Não informado'),
        ('residencial', 'Residencial'),
        ('comercial', 'Comercial'),
        ('rural', 'Rural'),
        ('condominio', 'Condomínio'),
    ]
    PERFIL_CHOICES = [
        ('', 'Não identificado'),
        ('comprador', 'Comprador'),
        ('investidor', 'Investidor'),
        ('empresa', 'Empresa (B2B)'),
        ('locatario', 'Locatário'),
    ]
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('em_contato', 'Em contato'),
        ('negociando', 'Negociando'),
        ('convertido', 'Convertido'),
        ('perdido', 'Perdido'),
    ]

    # Dados do contato
    nome = models.CharField('Nome', max_length=150)
    telefone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('E-mail', blank=True)
    mensagem = models.TextField('Mensagem', blank=True)

    # Classificação do lead
    operacao = models.CharField('Tipo de operação', max_length=20,
                                choices=OPERACAO_CHOICES, default='venda')
    tipo_imovel = models.CharField('Tipo do imóvel', max_length=20,
                                   choices=TIPO_IMOVEL_CHOICES, blank=True)
    perfil_cliente = models.CharField('Perfil do cliente', max_length=20,
                                      choices=PERFIL_CHOICES, blank=True)
    ticket_estimado = models.DecimalField('Ticket estimado (R$)', max_digits=14,
                                          decimal_places=2, null=True, blank=True)
    regiao = models.CharField('Região de interesse', max_length=100, blank=True)

    # Vínculos
    imovel = models.ForeignKey(Imovel, on_delete=models.SET_NULL,
                               null=True, blank=True,
                               verbose_name='Imóvel de interesse',
                               related_name='leads')
    corretor = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 verbose_name='Corretor responsável',
                                 related_name='leads')

    # Gestão
    status = models.CharField('Status', max_length=20,
                               choices=STATUS_CHOICES, default='novo')
    anotacoes = models.TextField('Anotações internas', blank=True)
    distribuido_automaticamente = models.BooleanField(default=False, editable=False)
    criado_em = models.DateTimeField('Recebido em', auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} — {self.get_operacao_display()}'

    @property
    def whatsapp_link(self):
        numero = self.telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not numero.startswith('55'):
            numero = '55' + numero
        return f'https://wa.me/{numero}'