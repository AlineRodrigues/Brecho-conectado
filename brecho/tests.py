from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Doacao,
    ItemVenda,
    MovimentacaoFinanceira,
    Produto,
    Venda,
)
from .services import finalizar_venda


class FinalizarVendaTest(TestCase):

    def setUp(self):
        self.doacao = Doacao.objects.create(
            data_recebimento=date(2026, 11, 13),
            descricao="Doação para testes",
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

    def test_confirmar_venda_com_dois_produtos(self):
        segundo_produto = Produto.objects.create(
            doacao=self.doacao,
            descricao="Calça Jeans de Teste",
            categoria="Vestuário",
            tamanho="40",
            cor="Preta",
            estado_conservacao="Bom",
            preco=Decimal("40.00"),
        )

        response = self.client.post(
            reverse("registrar_venda"),
            {
                "produto_ids": [
                    str(self.produto.pk),
                    str(segundo_produto.pk),
                ]
            },
        )

        venda = Venda.objects.get()

        self.assertRedirects(
            response,
            reverse("venda_sucesso", kwargs={"venda_id": venda.pk}),
        )

        self.produto.refresh_from_db()
        segundo_produto.refresh_from_db()

        self.assertEqual(self.produto.status, "vendido")
        self.assertEqual(segundo_produto.status, "vendido")
        self.assertEqual(venda.valor_total, Decimal("65.00"))
        self.assertEqual(venda.itens.count(), 2)

        movimentacao = MovimentacaoFinanceira.objects.get(venda=venda)
        self.assertEqual(movimentacao.tipo, "entrada")
        self.assertEqual(movimentacao.valor, Decimal("65.00"))
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 1)

    def test_impedir_reenvio_da_mesma_venda(self):
        dados_venda = {"produto_ids": [str(self.produto.pk)]}

        # Primeira confirmação: a venda deve ser registrada.
        primeira_resposta = self.client.post(
            reverse("registrar_venda"),
            dados_venda,
        )

        self.assertEqual(primeira_resposta.status_code, 302)

        # Segunda confirmação: o mesmo produto já está vendido.
        segunda_resposta = self.client.post(
            reverse("registrar_venda"),
            dados_venda,
        )

        self.assertEqual(segunda_resposta.status_code, 200)

        self.assertIn(
            "Um ou mais produtos não estão mais disponíveis.",
            segunda_resposta.context["erro"],
        )

        # Deve existir somente uma venda.
        self.assertEqual(Venda.objects.count(), 1)

        # Deve existir somente uma movimentação financeira.
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 1)

        # O produto deve continuar vendido.
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.status, "vendido")

    def test_impedir_confirmacao_sem_produtos(self):
        response = self.client.post(reverse("registrar_venda"), {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["erro"],
            "Selecione pelo menos um produto.",
        )

        self.produto.refresh_from_db()
        self.assertEqual(self.produto.status, "disponivel")
        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)

    def test_confirmar_venda_com_produto_disponivel(self):
        response = self.client.post(
            reverse("registrar_venda"),
            {"produto_ids": [str(self.produto.pk)]},
        )

        venda = Venda.objects.get()

        self.assertRedirects(
            response,
            reverse("venda_sucesso", kwargs={"venda_id": venda.pk}),
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
            reverse("registrar_venda"),
            {"produto_ids": [str(self.produto.pk)]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Um ou mais produtos não estão mais disponíveis.",
            response.context["erro"],
        )
        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)

    def test_impedir_confirmacao_com_identificador_invalido(self):
        response = self.client.post(
            reverse("registrar_venda"),
            {"produto_ids": ["abc"]},
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["erro"],
            "A seleção contém um identificador inválido.",
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.status, "disponivel")
        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)

    def test_impedir_confirmacao_com_produto_repetido(self):
        response = self.client.post(
            reverse("registrar_venda"),
            {
                "produto_ids": [
                    str(self.produto.pk),
                    str(self.produto.pk),
                ]
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["erro"],
            "A seleção contém produtos repetidos.",
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.status, "disponivel")
        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)

    def test_impedir_confirmacao_com_produto_inexistente(self):
        id_inexistente = self.produto.pk + 999

        response = self.client.post(
            reverse("registrar_venda"),
            {"produto_ids": [str(id_inexistente)]},
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "Um ou mais produtos não estão mais disponíveis.",
            response.context["erro"],
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.status, "disponivel")
        self.assertEqual(Venda.objects.count(), 0)
        self.assertEqual(MovimentacaoFinanceira.objects.count(), 0)


class VendaSucessoViewTest(TestCase):

    def setUp(self):
        self.hoje = timezone.localdate()

        self.venda = Venda.objects.create(
            valor_total=Decimal("65.00"),
        )

        self.doacao = Doacao.objects.create(
            data_recebimento=self.hoje,
            descricao="Doação para teste da confirmação",
        )

        self.produto = Produto.objects.create(
            doacao=self.doacao,
            descricao="Blusa Floral de Teste",
            categoria="Vestuário",
            tamanho="M",
            cor="Rosa",
            estado_conservacao="Bom",
            preco=Decimal("65.00"),
            status="vendido",
        )

        self.item = ItemVenda.objects.create(
            venda=self.venda,
            produto=self.produto,
            valor_unitario=Decimal("65.00"),
        )

        # Entrada financeira da venda
        MovimentacaoFinanceira.objects.create(
            venda=self.venda,
            data_movimentacao=self.hoje,
            tipo="entrada",
            descricao="Venda de teste",
            valor=Decimal("65.00"),
        )

        # Despesa do período
        MovimentacaoFinanceira.objects.create(
            data_movimentacao=self.hoje,
            tipo="despesa",
            descricao="Despesa de teste",
            valor=Decimal("10.00"),
        )

        # Destinação do período
        MovimentacaoFinanceira.objects.create(
            data_movimentacao=self.hoje,
            tipo="destinacao",
            descricao="Destinação de teste",
            valor=Decimal("5.00"),
        )

        # Movimentação anterior ao mês atual
        MovimentacaoFinanceira.objects.create(
            data_movimentacao=self.hoje.replace(day=1) - timedelta(days=1),
            tipo="despesa",
            descricao="Despesa do mês anterior",
            valor=Decimal("100.00"),
        )

        # Movimentação com data futura
        MovimentacaoFinanceira.objects.create(
            data_movimentacao=self.hoje + timedelta(days=1),
            tipo="despesa",
            descricao="Despesa futura",
            valor=Decimal("200.00"),
        )

    def test_exibir_resumo_financeiro_do_mes(self):
        response = self.client.get(
            reverse(
                "venda_sucesso",
                kwargs={"venda_id": self.venda.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["entradas_periodo"], Decimal("65.00"))
        self.assertEqual(response.context["despesas_periodo"], Decimal("10.00"))
        self.assertEqual(response.context["destinacoes_periodo"], Decimal("5.00"))
        self.assertEqual(response.context["saldo_periodo"], Decimal("50.00"))
        self.assertEqual(
            response.context["mes_referencia"],
            self.hoje.strftime("%m/%Y"),
        )

    def test_exibir_detalhes_dos_produtos_vendidos(self):
        response = self.client.get(
            reverse(
                "venda_sucesso",
                kwargs={"venda_id": self.venda.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["quantidade_itens"], 1)
        self.assertEqual(list(response.context["itens"]), [self.item])
        self.assertContains(response, "Blusa Floral de Teste")
        self.assertContains(response, "Rosa")
        self.assertContains(response, "R$ 65,00")

    def test_retornar_404_quando_venda_nao_existe(self):
        venda_inexistente_id = self.venda.pk + 1

        response = self.client.get(
            reverse(
                "venda_sucesso",
                kwargs={"venda_id": venda_inexistente_id},
            )
        )

        self.assertEqual(response.status_code, 404)
