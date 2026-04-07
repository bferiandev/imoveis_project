from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class Time(models.Model):
    """Times especializados da imobiliária."""
    TIPOS = [
        ('lancamentos', 'Lançamentos'),
        ('revenda', 'Revenda (Venda Pronta)'),
        ('locacao', 'Locação'),
        ('alto_padrao', 'Alto Padrão'),
        ('comercial', 'Comercial B2B'),
        ('investidor', 'Investidor'),
    ]
    nome = models.CharField('Nome', max_length=100)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    cor = models.CharField('Cor (hex)', max_length=7, default='#b8974a')

    class Meta:
        verbose_name = 'Time'
        verbose_name_plural = 'Times'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class RegraRoteamento(models.Model):
    """
    Regras que definem para qual time um lead é enviado.
    As regras são avaliadas em ordem de prioridade.
    """
    OPERACAO_CHOICES = [
        ('', 'Qualquer'),
        ('venda', 'Venda'),
        ('locacao', 'Locação'),
        ('lancamento', 'Lançamento'),
    ]
    TIPO_IMOVEL_CHOICES = [
        ('', 'Qualquer'),
        ('residencial', 'Residencial'),
        ('comercial', 'Comercial'),
        ('rural', 'Rural'),
        ('condominio', 'Condomínio'),
    ]
    PERFIL_CLIENTE_CHOICES = [
        ('', 'Qualquer'),
        ('comprador', 'Comprador'),
        ('investidor', 'Investidor'),
        ('empresa', 'Empresa (B2B)'),
        ('locatario', 'Locatário'),
    ]

    nome = models.CharField('Nome da regra', max_length=100)
    time = models.ForeignKey(Time, on_delete=models.CASCADE,
                             related_name='regras', verbose_name='Time destino')
    prioridade = models.PositiveIntegerField('Prioridade', default=0,
                                             help_text='Menor número = maior prioridade')

    # Critérios — todos em branco = aplica para qualquer lead
    operacao = models.CharField('Tipo de operação', max_length=20,
                                choices=OPERACAO_CHOICES, blank=True)
    tipo_imovel = models.CharField('Tipo do imóvel', max_length=20,
                                   choices=TIPO_IMOVEL_CHOICES, blank=True)
    perfil_cliente = models.CharField('Perfil do cliente', max_length=20,
                                      choices=PERFIL_CLIENTE_CHOICES, blank=True)
    ticket_min = models.DecimalField('Ticket mínimo (R$)', max_digits=14,
                                     decimal_places=2, null=True, blank=True)
    ticket_max = models.DecimalField('Ticket máximo (R$)', max_digits=14,
                                     decimal_places=2, null=True, blank=True)
    regiao = models.CharField('Região / Cidade', max_length=100, blank=True)
    ativa = models.BooleanField('Regra ativa', default=True)

    class Meta:
        verbose_name = 'Regra de Roteamento'
        verbose_name_plural = 'Regras de Roteamento'
        ordering = ['prioridade']

    def __str__(self):
        return f'{self.prioridade}. {self.nome} → {self.time}'


class PerfilCorretor(models.Model):
    """Perfil estendido do corretor com vínculo ao time."""
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='perfil')
    time = models.ForeignKey(Time, on_delete=models.SET_NULL,
                             null=True, blank=True,
                             related_name='corretores',
                             verbose_name='Time')
    creci = models.CharField('CRECI', max_length=20, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    foto = models.ImageField('Foto', upload_to='corretores/',
                             null=True, blank=True)
    ativo = models.BooleanField('Ativo (recebe leads)', default=True)
    posicao_fila = models.PositiveIntegerField('Posição na fila', default=0)
    bio = models.TextField('Bio', blank=True)
    total_leads_recebidos = models.PositiveIntegerField(default=0, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil do Corretor'
        verbose_name_plural = 'Perfis dos Corretores'
        ordering = ['posicao_fila', 'user__first_name']

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def nome_completo(self):
        return self.user.get_full_name() or self.user.username

    @property
    def is_admin(self):
        return self.user.is_staff


class LogAtividade(models.Model):
    ACAO_CHOICES = [
        ('criar', 'Criou'),
        ('editar', 'Editou'),
        ('excluir', 'Excluiu'),
        ('foto', 'Adicionou fotos'),
        ('status', 'Alterou status'),
        ('login', 'Fez login'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, related_name='logs')
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES)
    modelo = models.CharField(max_length=50)  # ex: 'Imóvel', 'Lead', 'Proprietário'
    objeto_id = models.PositiveIntegerField(null=True, blank=True)
    descricao = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Atividade'
        verbose_name_plural = 'Logs de Atividade'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.usuario} — {self.descricao}'