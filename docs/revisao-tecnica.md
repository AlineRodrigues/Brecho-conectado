# Revisão Técnica — Brechó Conectado

## 1. Escopo da revisão

Esta revisão considera a implementação do fluxo de registro e confirmação de vendas, incluindo os arquivos `models.py`, `services.py`, `views.py` e `tests.py` da aplicação `brecho`.

## 2. Arquitetura e modularização

O projeto utiliza uma arquitetura monolítica organizada segundo o padrão Model-Template-View (MTV) do Django. Os modelos representam as entidades e seus relacionamentos; as views recebem e processam as requisições; e o serviço `finalizar_venda()` concentra a regra de negócio responsável pela conclusão de uma venda.

A centralização dessa operação evita distribuir as regras de atualização do estoque e registro financeiro entre diferentes partes da aplicação. O uso de `transaction.atomic()` permite que a venda, seus itens, a alteração dos produtos e a movimentação financeira sejam confirmados em conjunto ou revertidos em caso de falha. O `select_for_update()` protege os produtos durante a operação, evitando que sejam vendidos simultaneamente por transações concorrentes.

Também foram utilizados relacionamentos `OneToOneField` para impedir que um mesmo produto seja associado a mais de um item de venda e para limitar a uma movimentação financeira associada por venda.

A arquitetura atual é adequada ao escopo do MVP. Otimizações adicionais de consultas devem ser avaliadas conforme o crescimento do volume de dados e medições de desempenho.

## 3. Qualidade, validação e segurança

A view de registro de vendas valida os identificadores recebidos, rejeitando seleções vazias, identificadores inválidos, produtos repetidos e produtos indisponíveis ou inexistentes. Os preços são recuperados do banco de dados, evitando confiar nos valores enviados pelo navegador.

O serviço também verifica se os produtos estão persistidos, se os valores são do tipo Decimal, finitos e maiores que zero, e se não há produtos repetidos na mesma operação. A utilização do ORM do Django evita a construção manual de consultas SQL por concatenação. O formulário utiliza proteção CSRF e as configurações sensíveis são carregadas por variáveis de ambiente.

A suíte atual possui 16 testes automatizados para as regras do serviço, as requisições da view e a apresentação do resultado da venda.

## 4. Limitações e melhorias futuras

A autenticação e o controle de permissões por perfil ainda não foram implementados. Também permanecem pendentes a configuração segura para produção, a execução de testes específicos de segurança e a validação completa dos requisitos de acessibilidade e desempenho.

Como melhoria futura, recomenda-se implementar autenticação e autorização, ampliar os testes de segurança e avaliar o desempenho das consultas financeiras com um conjunto maior de dados.

## 5. Conclusão

A revisão confirmou a separação das responsabilidades, a centralização das regras críticas de venda e a existência de mecanismos de consistência transacional e validação no servidor. Os testes automatizados oferecem evidências para o fluxo principal do MVP. As limitações identificadas foram registradas como melhorias futuras, sem considerar requisitos pendentes como funcionalidades concluídas.