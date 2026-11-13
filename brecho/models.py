from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Doacao(models.Model):
    id_doacao = models.AutoField(primary_key=True)
    data_recebimento = models.DateField()
    descricao = models.TextField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Doação {self.id_doacao} - {self.data_recebimento}"


class Produto(models.Model):
    STATUS_CHOICES = [
        ("disponivel", "Disponível"),
        ("vendido", "Vendido"),
    ]

    id_produto = models.AutoField(primary_key=True)
    doacao = models.ForeignKey(
        Doacao, on_delete=models.PROTECT, related_name="produtos"
    )
    descricao = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    tamanho = models.CharField(max_length=30, blank=True, null=True)
    cor = models.CharField(max_length=50)
    estado_conservacao = models.CharField(max_length=100)
    preco = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="disponivel"
    )

    def __str__(self):
        return f"{self.descricao} - {self.get_status_display()}"


class Venda(models.Model):
    id_venda = models.AutoField(primary_key=True)
    data_venda = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Venda {self.id_venda} - R$ {self.valor_total}"


class ItemVenda(models.Model):
    id_item_venda = models.AutoField(primary_key=True)
    venda = models.ForeignKey(Venda, on_delete=models.PROTECT, related_name="itens")
    produto = models.OneToOneField(
        Produto, on_delete=models.PROTECT, related_name="item_venda"
    )
    valor_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )

    def __str__(self):
        return f"{self.produto.descricao} - R$ {self.valor_unitario}"


class MovimentacaoFinanceira(models.Model):
    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("despesa", "Despesa"),
        ("destinacao", "Destinação"),
    ]

    id_movimentacao = models.AutoField(primary_key=True)
    venda = models.OneToOneField(
        Venda,
        on_delete=models.PROTECT,
        related_name="movimentacao",
        blank=True,
        null=True,
    )
    data_movimentacao = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    destino_recurso = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor}"
