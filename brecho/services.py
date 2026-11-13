from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import (
    Produto,
    Venda,
    ItemVenda,
    MovimentacaoFinanceira,
)


def finalizar_venda(produtos_e_valores, observacao=None):
    """
    Finaliza uma venda, atualiza o estoque e registra a entrada financeira.
    """

    if not produtos_e_valores:
        raise ValueError("A venda precisa ter pelo menos um produto.")

    produtos_ids = set()

    for produto, valor in produtos_e_valores:

        if not isinstance(produto, Produto) or produto.pk is None:
            raise ValueError(
                "Todos os produtos precisam estar cadastrados no banco de dados."
            )

        if not isinstance(valor, Decimal):
            raise ValueError("O valor de cada produto deve ser informado como Decimal.")

        if not valor.is_finite() or valor <= Decimal("0.00"):
            raise ValueError("O valor de cada produto deve ser maior que zero.")

        if produto.pk in produtos_ids:
            raise ValueError(
                f"O produto '{produto.descricao}' foi informado mais de uma vez."
            )

        produtos_ids.add(produto.pk)

    valor_total = sum((valor for produto, valor in produtos_e_valores), Decimal("0.00"))

    with transaction.atomic():

        produtos_bloqueados = []

        for produto, valor in produtos_e_valores:

            produto_bloqueado = Produto.objects.select_for_update().get(pk=produto.pk)

            if produto_bloqueado.status != "disponivel":
                raise ValueError(
                    f"O produto '{produto_bloqueado.descricao}' "
                    "não está mais disponível."
                )

            produtos_bloqueados.append((produto_bloqueado, valor))

        venda = Venda.objects.create(valor_total=valor_total, observacao=observacao)

        for produto, valor in produtos_bloqueados:
            ItemVenda.objects.create(venda=venda, produto=produto, valor_unitario=valor)

        for produto, valor in produtos_bloqueados:
            produto.status = "vendido"
            produto.save(update_fields=["status"])

        MovimentacaoFinanceira.objects.create(
            venda=venda,
            data_movimentacao=timezone.localdate(),
            tipo="entrada",
            descricao=f"Venda nº {venda.id_venda}",
            valor=valor_total,
        )

    return venda
