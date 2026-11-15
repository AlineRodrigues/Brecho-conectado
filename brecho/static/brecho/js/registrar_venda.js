
document.addEventListener("DOMContentLoaded", () => {
    // Elementos da tela
    const campoBusca = document.getElementById("busca-produto");
    const itensSelecionados = document.getElementById("itens-selecionados");
    const totalVenda = document.getElementById("total-venda");

    // Linhas dos produtos
    const linhasProdutos = document.querySelectorAll(".linha-produto");

    // Formata os valores no padrão brasileiro
    function formatarMoeda(valorEmCentavos) {
        return new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL"
        }).format(valorEmCentavos / 100);
    }

    // Atualiza os produtos selecionados e o total
    function atualizarResumo() {
        const produtosMarcados = document.querySelectorAll(
            ".produto-selecao:checked"
        );

        itensSelecionados.replaceChildren();

        let totalEmCentavos = 0;

        if (produtosMarcados.length === 0) {
            const mensagemVazia = document.createElement("p");

            mensagemVazia.className = "resumo-vazio";
            mensagemVazia.textContent = "Nenhum produto selecionado.";

            itensSelecionados.appendChild(mensagemVazia);
            totalVenda.textContent = formatarMoeda(0);

            return;
        }

        produtosMarcados.forEach((checkbox) => {
            const descricao = checkbox.dataset.description;
            const preco = Number(checkbox.dataset.price);

            if (!Number.isFinite(preco)) {
                return;
            }

            const precoEmCentavos = Math.round(preco * 100);
            totalEmCentavos += precoEmCentavos;

            const linhaResumo = document.createElement("div");
            linhaResumo.className = "item-selecionado";

            const nomeProduto = document.createElement("span");
            nomeProduto.textContent = descricao;

            const precoProduto = document.createElement("strong");
            precoProduto.textContent = formatarMoeda(precoEmCentavos);

            linhaResumo.appendChild(nomeProduto);
            linhaResumo.appendChild(precoProduto);

            itensSelecionados.appendChild(linhaResumo);
        });

        totalVenda.textContent = formatarMoeda(totalEmCentavos);
    }

    // Pesquisa produtos pela descrição
    campoBusca.addEventListener("input", () => {
        const termo = campoBusca.value.trim().toLocaleLowerCase("pt-BR");

        linhasProdutos.forEach((linha) => {
            const descricao = linha.cells[1].textContent
                .trim()
                .toLocaleLowerCase("pt-BR");

            linha.hidden = !descricao.includes(termo);
        });
    });

    // Atualiza o resumo ao selecionar ou desmarcar produtos
    document.querySelectorAll(".produto-selecao").forEach((checkbox) => {
        checkbox.addEventListener("change", atualizarResumo);
    });

    // Inicializa o resumo
    atualizarResumo();
});
