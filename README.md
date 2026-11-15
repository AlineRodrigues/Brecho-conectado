# Brechó Conectado

Aplicação web em desenvolvimento para apoiar a gestão do brechó solidário da **Paróquia São José de Pirituba**, em São Paulo (SP). O projeto faz parte das atividades práticas da disciplina Projeto de Software e busca substituir controles manuais por registros digitais organizados de doações, produtos, estoque, vendas e movimentações financeiras.

> **Estado do projeto:** implementação incremental do MVP. O fluxo de registro e confirmação de vendas está implementado e coberto por testes automatizados. As demais funcionalidades e requisitos não funcionais estão em diferentes estágios de implementação, conforme a matriz abaixo.

## 1. Contexto e problema

O diagnóstico realizado na Experiência Prática 1 identificou que o brechó recebe doações de roupas e acessórios, mas o controle das peças, do estoque, das vendas e dos valores arrecadados é realizado manualmente, principalmente em cadernos e anotações. Isso dificulta centralizar e consultar informações, acompanhar a disponibilidade dos produtos e consolidar as movimentações financeiras.

O público direto do sistema é formado pelos membros e voluntários responsáveis pelo recebimento das doações, organização das peças, controle do estoque, registro das vendas e acompanhamento financeiro. Doadores, compradores, projetos sociais apoiados pela paróquia e a comunidade local são beneficiários indiretos.

## 2. Objetivo e conexão com o ODS

O objetivo é oferecer uma aplicação web simples e responsiva que centralize os registros necessários à operação do brechó, facilitando a organização dos produtos e o acompanhamento dos recursos arrecadados.

O projeto se relaciona ao **ODS 12 — Consumo e Produção Responsáveis**, especialmente à **Meta 12.5**, por apoiar a reutilização e a comercialização de peças doadas, contribuindo para prolongar sua vida útil e reduzir o descarte. O sistema apoia a organização dessa atividade; seu impacto depende da utilização efetiva pela instituição.

## 3. Escopo do MVP e requisitos priorizados

A Experiência Prática 2 definiu seis requisitos funcionais. Os requisitos **RF01 a RF05 são obrigatórios** para o MVP. O **RF06 é desejável** e foi planejado como evolução posterior.

| ID | Prioridade | Requisito definido na Atividade 2 | Situação atual da implementação |
|---|---|---|---|
| **RF01** | Obrigatório | Registrar o recebimento de doações, com data, descrição e identificador único. | **Parcial.** O modelo `Doacao` existe. Ainda falta implementar a tela, a rota e o fluxo de cadastro e consulta de doações. |
| **RF02** | Obrigatório | Cadastrar individualmente cada peça, com descrição, categoria, tamanho, cor, estado de conservação, preço e status, vinculando-a a uma doação. | **Parcial.** O modelo `Produto`, seus campos, o vínculo com `Doacao`, as opções de status e a validação de preço estão modelados. Ainda falta implementar o fluxo de cadastro pela interface. |
| **RF03** | Obrigatório | Consultar produtos, apresentando descrição, categoria, tamanho, cor, preço e status, para identificar a disponibilidade. | **Parcial.** A tela de registro de venda lista os produtos disponíveis e permite pesquisá-los. Ainda falta uma tela própria de consulta geral do estoque, incluindo produtos disponíveis e vendidos. |
| **RF04** | Obrigatório | Registrar venda de um ou mais produtos disponíveis, calcular o total e atualizar automaticamente o status para vendido. A confirmação deve gerar uma entrada financeira sem duplicidade. | **Implementado no fluxo principal.** A tela envia os produtos selecionados; o servidor valida a solicitação; o serviço finaliza a venda em transação; os produtos passam para `vendido`; e uma entrada financeira é criada. O fluxo possui testes automatizados. |
| **RF05** | Obrigatório | Registrar despesas e destinações, com data, tipo, descrição e valor; o destino deve ser informado para uma destinação. | **Parcial.** O modelo `MovimentacaoFinanceira` contempla os tipos `entrada`, `despesa` e `destinacao`, além do campo de destino. A entrada da venda é criada automaticamente. Ainda faltam telas, rotas e validações condicionais para lançamento manual de despesas e destinações. |
| **RF06** | Desejável | Disponibilizar relatórios financeiros por período, totalizando entradas de vendas, despesas e destinações sem duplicidade. | **Evolução parcial.** A confirmação da venda exibe um resumo do mês corrente. Ainda não existe relatório independente com seleção de período. O requisito permanece como evolução desejável. |

### 3.1 Histórias de usuário relacionadas

- Como voluntário responsável pelas doações, quero registrar as doações recebidas e identificar os produtos associados, para manter um histórico organizado.
- Como voluntário responsável pelo estoque, quero cadastrar e consultar individualmente as peças e suas situações, para saber quais estão disponíveis.
- Como responsável pelo controle financeiro, quero registrar vendas, despesas e destinações, para acompanhar os recursos arrecadados e sua aplicação.

## 4. Matriz de rastreabilidade da implementação

A matriz relaciona os requisitos originais da Atividade 2 aos elementos existentes no código. Quando uma rota ou tela ainda não foi implementada, isso é indicado explicitamente em vez de apresentar o requisito como concluído.

| Requisito | Modelos envolvidos | Rotas / interface atuais | Regras e validações implementadas | Evidências de teste atuais |
|---|---|---|---|---|
| **RF01 — Doações** | `Doacao` | Ainda não há rota ou tela própria de cadastro de doação. | O modelo armazena data, descrição e observação; o identificador é gerado pelo Django. | Ainda não há teste de fluxo de cadastro pela interface. |
| **RF02 — Cadastro de produtos** | `Doacao`, `Produto` | Ainda não há rota ou formulário próprio de cadastro de produtos. | Produto relacionado a uma doação; status com opções `disponivel` e `vendido`; preço validado para não ser negativo. | Os produtos são criados nos cenários de teste; falta teste do cadastro por uma futura view/formulário. |
| **RF03 — Consulta de estoque** | `Produto` | `/vendas/registrar/` apresenta produtos disponíveis para seleção. A rota própria de consulta geral ainda não existe. | A listagem do fluxo de venda filtra produtos com status `disponivel`; a busca da tela filtra a descrição no navegador. | Os testes da view de vendas verificam produtos disponíveis e indisponíveis; ainda falta teste da futura consulta geral do estoque. |
| **RF04 — Registro de vendas** | `Produto`, `Venda`, `ItemVenda`, `MovimentacaoFinanceira` | `GET/POST /vendas/registrar/`; `GET /vendas/<id>/sucesso/`. | Rejeita seleção vazia, identificadores não numéricos, IDs repetidos e produtos indisponíveis/inexistentes. O serviço usa `transaction.atomic()` e `select_for_update()`. Os produtos são atualizados para `vendido` e uma entrada é associada à venda. | Testes de venda com um e dois produtos, produto já vendido, seleção repetida, identificador inválido/inexistente, reenvio da seleção e consistência da movimentação. |
| **RF05 — Despesas e destinações** | `MovimentacaoFinanceira` | Ainda não há rota ou tela para lançamento manual de despesas e destinações. | O modelo possui tipos `entrada`, `despesa` e `destinacao`, valor positivo e campo `destino_recurso`. A obrigatoriedade condicional do destino ainda precisa ser implementada. | O teste do resumo financeiro utiliza registros de despesa e destinação criados no cenário de teste; ainda falta teste do fluxo de lançamento manual. |
| **RF06 — Relatórios por período** | `MovimentacaoFinanceira` | A rota de confirmação apresenta totais do mês corrente; não há rota de relatório independente nem seletor de período. | A view filtra movimentações do primeiro dia do mês até a data local atual e calcula entradas, despesas, destinações e saldo. | `test_exibir_resumo_financeiro_do_mes` verifica os totais e a exclusão de datas fora do período. O requisito completo de relatório por período permanece futuro. |

### 4.1 Fluxo central implementado — RF04

1. O voluntário acessa `/vendas/registrar/` e visualiza os produtos disponíveis.
2. A interface permite selecionar um ou mais produtos e apresenta o resumo e o total calculado no navegador.
3. Ao confirmar, o navegador envia os identificadores dos produtos por uma requisição `POST` protegida por CSRF.
4. A view valida se a seleção não está vazia, se os identificadores são numéricos e únicos e se todos os produtos continuam disponíveis.
5. O serviço `finalizar_venda()` revalida a disponibilidade dentro de uma transação, cria a venda e seus itens, atualiza o status dos produtos e registra a entrada financeira.
6. Se a operação for concluída, o sistema redireciona para `/vendas/<id>/sucesso/`, que apresenta os detalhes da venda e o resumo financeiro do mês. Se a validação falhar, a operação não é concluída e uma mensagem é apresentada.

A seleção temporária no navegador não altera o estoque. A alteração ocorre somente na finalização da venda no servidor.

## 5. Modelagem de dados

A modelagem da Atividade 2 prevê cinco entidades principais, implementadas como modelos Django:

| Modelo | Finalidade | Relacionamentos principais |
|---|---|---|
| `Doacao` | Registrar o recebimento de doações. | Uma doação pode estar relacionada a vários produtos. |
| `Produto` | Registrar individualmente cada peça e seu status no estoque. | Cada produto pertence a uma doação; pode estar associado a, no máximo, um `ItemVenda`. |
| `Venda` | Registrar data e valor total da operação. | Uma venda possui vários itens de venda. |
| `ItemVenda` | Relacionar um produto à venda e guardar o valor unitário praticado. | Liga `Venda` e `Produto`; o produto usa relacionamento `OneToOneField` com `ItemVenda`. |
| `MovimentacaoFinanceira` | Registrar entradas, despesas e destinações. | A movimentação associada à venda usa `OneToOneField`, limitando a uma movimentação por venda. |

Os valores monetários são representados por `DecimalField`. O serviço de vendas utiliza uma transação atômica para que a criação da venda, dos itens, a atualização do estoque e o registro da entrada sejam confirmados em conjunto ou revertidos em caso de erro.

Como medida de minimização de dados prevista na Atividade 2, o sistema não precisa coletar CPF, endereço ou telefone dos doadores para executar as funções do MVP.

## 6. Arquitetura e tecnologias

A arquitetura planejada é monolítica em camadas, utilizando a estrutura **Model-Template-View (MTV) do Django**. As responsabilidades ficam organizadas entre interface, processamento das regras de negócio e persistência.

| Tecnologia | Uso no projeto |
|---|---|
| Python | Linguagem da aplicação e das regras de negócio. |
| Django | Framework web, rotas, views, templates, ORM, validações e testes. |
| PostgreSQL | Banco de dados relacional. |
| Psycopg | Adaptador de comunicação entre Django e PostgreSQL. |
| HTML e CSS | Estrutura e apresentação das telas. |
| JavaScript | Busca de produtos, seleção temporária e cálculo do resumo na tela de venda. |
| `python-dotenv` | Carregamento das configurações mantidas em variáveis de ambiente. |

**Observação sobre o planejamento e o ambiente atual:** a Atividade 2 previa Python 3.12, Django 5.2 LTS e Bootstrap 5.3. O ambiente de desenvolvimento atualmente utilizado está baseado em Python 3.14.2, Django 5.2.19, PostgreSQL 17.11, Psycopg 3.3.8 e `python-dotenv` 1.2.4. As telas atuais utilizam CSS próprio e JavaScript, sem integração de Bootstrap até o momento. A compatibilidade das versões e a configuração de produção deverão ser verificadas antes da implantação.

### 6.1 Estrutura principal do código

```text
Brecho-conectado/
├── config/
│   ├── settings.py
│   └── urls.py
├── brecho/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── templates/
│   │   └── brecho/
│   │       ├── inicio.html
│   │       ├── registrar_venda.html
│   │       └── venda_sucesso.html
│   └── static/
│       └── brecho/
│           ├── css/estilo.css
│           ├── js/registrar_venda.js
│           └── img/
├── manage.py
└── README.md
```

## 7. Rotas implementadas

| Método | Caminho | Finalidade |
|---|---|---|
| `GET` | `/` | Apresenta a tela inicial/menu. |
| `GET` e `POST` | `/vendas/registrar/` | Lista produtos disponíveis e processa a confirmação de venda. |
| `GET` | `/vendas/<id>/sucesso/` | Apresenta os detalhes da venda e o resumo financeiro do mês. |
| Conforme configuração do Django | `/admin/` | Área administrativa padrão do Django. |

As opções de menu para cadastro de doações, cadastro de produtos, consulta geral de estoque e movimentações financeiras ainda não possuem seus fluxos completos implementados.

## 8. Testes automatizados

A suíte atual contém **16 testes automatizados**, executados com `python manage.py test`. Na última execução registrada durante o desenvolvimento, os 16 testes passaram.

Os testes estão organizados em três grupos:

- `FinalizarVendaTest`: verifica as regras do serviço, incluindo venda com dois produtos, produto já vendido, venda vazia, produto repetido e preço zero.
- `RegistrarVendaViewTest`: verifica o fluxo HTTP, venda com um ou dois produtos, seleção vazia, produto indisponível, identificador inválido, produto repetido, produto inexistente e reenvio da mesma seleção.
- `VendaSucessoViewTest`: verifica os detalhes dos produtos vendidos, os totais financeiros do mês e a resposta 404 para uma venda inexistente.

Os testes usam banco temporário criado pelo Django. Eles não substituem a validação prática com o representante do brechó nem os testes de segurança, acessibilidade, desempenho e implantação previstos na Atividade 2.

## 9. Requisitos não funcionais e estado de verificação

| ID | Requisito da Atividade 2 | Situação atual |
|---|---|---|
| **RNF01 — Autenticação e hash robusto** | Acesso restrito a usuários autenticados, permissões por perfil, senhas com hash robusto, gestão de sessão e logout. | **Pendente de implementação.** O cabeçalho atual apresenta uma identificação visual de voluntário, mas não representa um fluxo de autenticação implementado. Não publicar a aplicação como sistema multiusuário antes de implementar e testar autenticação e autorização. |
| **RNF02 — OWASP e proteção de dados** | Validação no servidor, proteção contra acesso indevido, injeção, XSS e CSRF; segredos fora do código; configuração segura em produção. | **Parcial.** O formulário de venda usa CSRF, as consultas utilizam Django ORM e o fluxo de venda valida os dados no servidor. A configuração local carrega segredos por variável de ambiente. Autenticação, permissões, limitação de tentativas de login, HTTPS, configuração de produção e testes específicos OWASP ainda precisam ser implementados/verificados. |
| **RNF03 — Desempenho e portabilidade** | Aplicação web reproduzível em hospedagem compatível; meta de LCP de até 3 segundos na mediana de cinco medições, em smartphone 4G e conjunto de dados especificado na Atividade 2. | **Pendente de validação.** O projeto foi executado localmente. Ainda não há implantação documentada nem evidência das cinco medições de desempenho com o volume de dados definido. |
| **RNF04 — Acessibilidade e facilidade de operação** | Layout responsivo, contraste mínimo, ampliação até 200%, teclado e foco visível, rótulos associados, erros claros, controles com área mínima de 44 × 44 px e alertas que não dependam só da cor. | **Parcial.** As telas principais foram adaptadas e inspecionadas em desktop e em viewport móvel. Há textos, rótulos, símbolos e mensagens. A auditoria de contraste, ampliação de 200%, navegação integral por teclado, foco visível, leitores de tela e dimensões mínimas de todos os controles ainda precisa ser concluída. A tabela de produtos utiliza rolagem horizontal em telas estreitas, ponto a avaliar frente ao critério de não perda de conteúdo. |

## 10. Limites de escopo

Conforme as atividades acadêmicas, não fazem parte do MVP inicial:

- Integração com bancos, Pix, maquininhas, gateways ou plataformas de pagamento.
- Loja virtual pública, pedidos ou compras on-line.
- Aplicativo nativo Android/iOS, leitura de código de barras, notificações automáticas e integrações externas avançadas.
- Relatórios financeiros completos por período (RF06), classificados como desejáveis e planejados para evolução posterior.

## 11. Plano de validação com o público externo

A Atividade 2 prevê uma validação individual com uma voluntária do Brechó Solidário da Paróquia São José de Pirituba, mantendo sua identidade preservada. A data prevista no planejamento é **30/01/2027**. A sessão deverá utilizar dados fictícios e registrar dispositivo e condições de conexão.

As três tarefas planejadas são:

1. **Localizar o registro de venda:** encontrar a opção e chegar à tela de seleção em até 1 minuto.
2. **Registrar uma venda fictícia:** selecionar a peça indicada, conferir o total e concluir o fluxo em até 3 minutos.
3. **Interpretar o resultado e verificar acessibilidade:** identificar a confirmação, o status do produto, o valor e as opções de continuidade em até 2 minutos.

Os critérios de aceitação definidos na Atividade 2 são: 100% de sucesso independente nas três tarefas; conclusão correta do fluxo de venda em até 180 segundos; e satisfação mínima de 4 em uma escala de 1 a 5. Esses critérios ainda deverão ser medidos com a participante. A aprovação nos testes automatizados não substitui essa validação prática.

## 12. Como executar localmente

### Pré-requisitos

- Python instalado.
- PostgreSQL instalado e em execução.
- Banco e usuário PostgreSQL configurados para a aplicação.
- Arquivo `.env` local com as configurações necessárias. Não compartilhe nem versiona esse arquivo.

### Ambiente virtual (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências utilizadas no ambiente de desenvolvimento, conforme as versões registradas no projeto:

```powershell
pip install "Django==5.2.19" "psycopg[binary]==3.3.8" "python-dotenv==1.2.4"
```

### Variáveis de ambiente

O arquivo `.env`, na raiz do projeto, deve fornecer as configurações abaixo. Preencha os valores localmente; não coloque senhas ou chaves reais no README ou no Git:

```dotenv
SECRET_KEY=substitua_por_uma_chave_local
DB_NAME=brecho_conectado
DB_USER=seu_usuario_postgresql
DB_PASSWORD=sua_senha_postgresql
DB_HOST=localhost
DB_PORT=5432
```

Crie previamente o banco e o usuário no PostgreSQL, conforme a configuração do ambiente local.

### Migrações, verificações e servidor

```powershell
python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver
```

Com o servidor ativo, as rotas principais ficam disponíveis em:

- Tela inicial: `http://127.0.0.1:8000/`
- Registrar venda: `http://127.0.0.1:8000/vendas/registrar/`
- Confirmação de uma venda: `http://127.0.0.1:8000/vendas/1/sucesso/` (substitua `1` por um identificador existente).

## 13. Próximas etapas

1. Implementar cadastro e consulta de doações (RF01).
2. Implementar cadastro de produtos pela interface (RF02).
3. Implementar consulta geral do estoque (RF03).
4. Implementar formulários e rotas para despesas e destinações, incluindo a obrigatoriedade do destino nas destinações (RF05).
5. Implementar autenticação, autorização e controles de segurança previstos nos RNF01 e RNF02.
6. Concluir a verificação de acessibilidade (RNF04).
7. Implantar em ambiente compatível e executar os testes de portabilidade e desempenho (RNF03).
8. Realizar a validação prática com a voluntária e registrar os resultados.
9. Avaliar a evolução dos relatórios financeiros por período (RF06).

---

**Projeto acadêmico:** Projeto de Software — Experiências Práticas 1 e 2\
**Parceiro comunitário:** Brechó Solidário da Paróquia São José de Pirituba\
**ODS relacionado:** ODS 12 — Meta 12.5
