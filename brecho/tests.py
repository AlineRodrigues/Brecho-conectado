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

from django.urls import reverse


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


class RegistrarVendaViewTest(TestCase):

    def setUp(self):
        self.doacao = Doacao.objects.create(
            data_recebimento=date(2026, 11, 14),
            descricao="Doação para teste da tela de vendas",
        )

        self.produto = Produto.objects.create(
            doacao=self.doacao,
            descricao="Camisa de Teste",
            categoria="Vestuário",
            tamanho="M",
            cor="Azul",
            estado_conservacao="Bom",
            preco=Decimal("25.00"),
        )

    def test_impedir_confirmacao_sem_produtos(self):
        response = self.client.post(reverse("registrar_venda"), {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["erro"], "Selecione pelo menos um produto.")

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.status, "disponivel")
        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)

    def test_confirmar_venda_com_produto_disponivel(self):
        response = self.client.post(
            reverse("registrar_venda"), {"produto_ids": [str(self.produto.pk)]}
        )

        venda = Venda.objects.get()

        self.assertRedirects(
            response, reverse("venda_sucesso", kwargs={"venda_id": venda.pk})
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.status, "vendido")
        self.assertEqual(venda.valor_total, Decimal("25.00"))
        self.assertEqual(venda.itens.count(), 1)

        movimentacao = MovimentacaoFinanceira.objects.get(venda=venda)

        self.assertEqual(movimentacao.tipo, "entrada")
        self.assertEqual(movimentacao.valor, Decimal("25.00"))

    def test_impedir_confirmacao_de_produto_indisponivel(self):
        self.produto.status = "vendido"
        self.produto.save(update_fields=["status"])

        response = self.client.post(
            reverse("registrar_venda"), {"produto_ids": [str(self.produto.pk)]}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Um ou mais produtos não estão mais disponíveis.", response.context["erro"]
        )

        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)