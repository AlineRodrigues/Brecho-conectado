from datetime import date
from decimal import Decimal

from django.test import TestCase

from .models import (
    Doacao,
    Produto,
    Venda,
    ItemVenda,
    MovimentacaoFinanceira,
)

from .services import finalizar_venda


class FinalizarVendaTest(TestCase):

    def setUp(self):
        self.doacao = Doacao.objects.create(
            data_recebimento=date(2026, 11, 13), descricao="Doação para testes"
        )

        self.produto1 = Produto.objects.create(
            doacao=self.doacao,
            descricao="Camisa",
            categoria="Roupa",
            tamanho="M",
            cor="Azul",
            estado_conservacao="Bom",
            preco=Decimal("20.00"),
        )

        self.produto2 = Produto.objects.create(
            doacao=self.doacao,
            descricao="Calça",
            categoria="Roupa",
            tamanho="40",
            cor="Preta",
            estado_conservacao="Bom",
            preco=Decimal("35.00"),
        )

    def test_finalizar_venda_com_dois_produtos(self):
        venda = finalizar_venda(
            [
                (self.produto1, Decimal("20.00")),
                (self.produto2, Decimal("35.00")),
            ]
        )

        self.assertEqual(venda.valor_total, Decimal("55.00"))

        self.produto1.refresh_from_db()
        self.produto2.refresh_from_db()

        self.assertEqual(self.produto1.status, "vendido")
        self.assertEqual(self.produto2.status, "vendido")

        self.assertEqual(venda.itens.count(), 2)

        movimentacao = MovimentacaoFinanceira.objects.get(venda=venda)

        self.assertEqual(movimentacao.tipo, "entrada")
        self.assertEqual(movimentacao.valor, Decimal("55.00"))

    def test_impedir_venda_de_produto_ja_vendido(self):
        self.produto2.status = "vendido"
        self.produto2.save()

        with self.assertRaises(ValueError):
            finalizar_venda(
                [
                    (self.produto1, Decimal("20.00")),
                    (self.produto2, Decimal("35.00")),
                ]
            )

        self.produto1.refresh_from_db()
        self.produto2.refresh_from_db()

        self.assertEqual(self.produto1.status, "disponivel")
        self.assertEqual(self.produto2.status, "vendido")

        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)

    def test_impedir_venda_sem_produtos(self):
        with self.assertRaises(ValueError):
            finalizar_venda([])

        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(ItemVenda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)

    def test_impedir_produto_repetido_na_mesma_venda(self):
        with self.assertRaises(ValueError):
            finalizar_venda(
                [
                    (self.produto1, Decimal("20.00")),
                    (self.produto1, Decimal("20.00")),
                ]
            )

        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(ItemVenda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)

    def test_impedir_venda_com_preco_zero(self):
        with self.assertRaises(ValueError):
            finalizar_venda([(self.produto1, Decimal("0.00"))])

        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)
