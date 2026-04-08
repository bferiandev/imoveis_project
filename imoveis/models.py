from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Proprietario(models.Model):
    TIPO_CHOICES = [
        ('pf', 'Pessoa Física'),
        ('pj', 'Pessoa Jurídica'),
    ]

    nome = models.CharField('Nome completo', max_length=200)
    tipo = models.CharField('Tipo', max_length=2, choices=TIPO_CHOICES, default='pf')
    cpf_cnpj = models.CharField('CPF / CNPJ', max_length=20, blank=True)
    telefone = models.CharField('Telefone', max_length=20)
    telefone2 = models.CharField('Telefone 2', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Proprietário'
        verbose_name_plural = 'Proprietários'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, default='SP')

    class Meta:
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome}/{self.estado}'


class Bairro(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name='bairros')

    class Meta:
        verbose_name = 'Bairro'
        verbose_name_plural = 'Bairros'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} — {self.cidade.nome}'


class Imovel(models.Model):
    TIPO_CHOICES = [
        ('apartamento', 'Apartamento'),
        ('casa', 'Casa'),
        ('cobertura', 'Cobertura'),
        ('terreno', 'Terreno'),
        ('comercial', 'Comercial'),
    ]
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('vendido', 'Vendido'),
        ('alugado', 'Alugado'),
        ('reservado', 'Reservado'),
    ]
    DESTAQUE_CHOICES = [
        ('', 'Nenhum'),
        ('destaque', 'Destaque'),
        ('novo', 'Novo'),
        ('oportunidade', 'Oportunidade'),
        ('exclusivo', 'Exclusivo'),
    ]

    # Identificação
    titulo = models.CharField('Título', max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='apartamento')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    destaque = models.CharField(max_length=20, choices=DESTAQUE_CHOICES, blank=True)

    # Localização
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True)
    endereco = models.CharField('Endereço', max_length=300, blank=True)
    cep = models.CharField('CEP', max_length=9, blank=True)

    # Preço
    preco = models.DecimalField('Preço (R$)', max_digits=14, decimal_places=2)
    preco_negociavel = models.BooleanField('Preço negociável', default=False)
    condominio = models.DecimalField('Condomínio (R$)', max_digits=10, decimal_places=2, null=True, blank=True)
    iptu = models.DecimalField('IPTU mensal (R$)', max_digits=10, decimal_places=2, null=True, blank=True)

    # Características
    area_total = models.PositiveIntegerField('Área total (m²)', null=True, blank=True)
    area_construida = models.PositiveIntegerField('Área construída (m²)', null=True, blank=True)
    quartos = models.PositiveSmallIntegerField('Quartos', null=True, blank=True)
    suites = models.PositiveSmallIntegerField('Suítes', null=True, blank=True)
    banheiros = models.PositiveSmallIntegerField('Banheiros', null=True, blank=True)
    vagas = models.PositiveSmallIntegerField('Vagas de garagem', null=True, blank=True)
    andar = models.PositiveSmallIntegerField('Andar', null=True, blank=True)

    # Descrição
    descricao = models.TextField('Descrição')
    diferenciais = models.TextField('Diferenciais (um por linha)', blank=True,
                                    help_text='Digite cada diferencial em uma linha separada')

    # SEO
    meta_descricao = models.CharField('Meta descrição (SEO)', max_length=160, blank=True)

    # Controle
    ativo = models.BooleanField('Ativo (visível no site)', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    visualizacoes = models.PositiveIntegerField(default=0, editable=False)

    # PROPRIETÁRIO
    proprietario = models.ForeignKey(
    'Proprietario',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    verbose_name='Proprietário',
    related_name='imoveis'
    )

    class Meta:
        verbose_name = 'Imóvel'
        verbose_name_plural = 'Imóveis'
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)
            slug = base
            n = 1
            while Imovel.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('imoveis:detalhe', kwargs={'slug': self.slug})

    @property
    def preco_formatado(self):
        v = float(self.preco)
        if v >= 1_000_000:
            # Verifica se é valor exato em milhões
            milhoes = v / 1_000_000
            if milhoes == int(milhoes):
                # Ex: 2.000.000 → R$ 2 milhões
                return f"R$ {int(milhoes):,} milhão{'s' if int(milhoes) > 1 else ''}".replace(',', '.')
            elif v % 100_000 == 0:
                # Ex: 1.500.000 → R$ 1,5 milhão
                return f"R$ {milhoes:.1f} milhão".replace('.', ',')
            else:
                # Ex: 1.350.000 → R$ 1.350.000
                return f"R$ {v:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"R$ {v:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    @property
    def foto_principal(self):
        foto = self.fotos.filter(principal=True).first() or self.fotos.first()
        return foto

    @property
    def lista_diferenciais(self):
        return [d.strip() for d in self.diferenciais.splitlines() if d.strip()]


class FotoImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField('Foto', upload_to='imoveis/')
    legenda = models.CharField(max_length=200, blank=True)
    principal = models.BooleanField('Foto principal', default=False)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'
        ordering = ['-principal', 'ordem']

    def __str__(self):
        return f'Foto de {self.imovel.titulo}'

    def save(self, *args, **kwargs):
        # garante somente 1 principal por imóvel
        if self.principal:
            FotoImovel.objects.filter(imovel=self.imovel, principal=True).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)
