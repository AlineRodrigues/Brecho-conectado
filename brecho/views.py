
from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import MovimentacaoFinanceira, Produto, Venda
from .services import finalizar_venda


def inicio(request):
    return render(request, "brecho/inicio.html")


def registrar_venda(request):
    erro = None

    if request.method == "POST":
        ids_recebidos = request.POST.getlist("produto_ids")

        if not ids_recebidos:
            erro = "Selecione pelo menos um produto."

        elif not all(id_produto.isdecimal() for id_produto in ids_recebidos):
            erro = "A seleção contém um identificador inválido."

        elif len(ids_recebidos) != len(set(ids_recebidos)):
            erro = "A seleção contém produtos repetidos."

        else:
            produtos_encontrados = Produto.objects.filter(
                pk__in=ids_recebidos,
                status="disponivel"
            )

            produtos_por_id = {
                str(produto.pk): produto
                for produto in produtos_encontrados
            }

            if len(produtos_por_id) != len(ids_recebidos):
                erro = (
                    "Um ou mais produtos não estão mais disponíveis. "
                    "Atualize a página e confira o estoque."
                )

            else:
                produtos_e_valores = [
                    (
                        produtos_por_id[id_produto],
                        produtos_por_id[id_produto].preco
                    )
                    for id_produto in ids_recebidos
                ]

                try:
                    venda = finalizar_venda(produtos_e_valores)

                except (ValueError, Produto.DoesNotExist) as exc:
                    erro = str(exc)

                else:
                    return redirect(
                        "venda_sucesso",
                        venda_id=venda.pk
                    )

    produtos = Produto.objects.filter(
        status="disponivel"
    ).order_by("descricao")

    return render(
        request,
        "brecho/registrar_venda.html",
        {
            "produtos": produtos,
            "erro": erro
        }
    )


def venda_sucesso(request, venda_id):
    venda = get_object_or_404(Venda, pk=venda_id)

    itens = venda.itens.select_related("produto").all()

    # Define o período financeiro: mês atual até hoje.
    hoje = timezone.localdate()
    inicio_periodo = hoje.replace(day=1)

    movimentacoes = MovimentacaoFinanceira.objects.filter(
        data_movimentacao__gte=inicio_periodo,
        data_movimentacao__lte=hoje
    )

    entradas = sum(
        movimentacoes.filter(tipo="entrada").values_list("valor", flat=True),
        Decimal("0.00")
    )

    despesas = sum(
        movimentacoes.filter(tipo="despesa").values_list("valor", flat=True),
        Decimal("0.00")
    )

    destinacoes = sum(
        movimentacoes.filter(tipo="destinacao").values_list("valor", flat=True),
        Decimal("0.00")
    )

    saldo_periodo = entradas - despesas - destinacoes

    contexto = {
        "venda": venda,
        "itens": itens,
        "quantidade_itens": itens.count(),
        "entradas_periodo": entradas,
        "despesas_periodo": despesas,
        "destinacoes_periodo": destinacoes,
        "saldo_periodo": saldo_periodo,
        "mes_referencia": hoje.strftime("%m/%Y"),
        "inicio_periodo": inicio_periodo,
        "fim_periodo": hoje,
    }

    return render(
        request,
        "brecho/venda_sucesso.html",
        contexto
    )
