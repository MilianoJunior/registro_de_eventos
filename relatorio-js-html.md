# Relatório — HTML gerado via JavaScript e classes embutidas

## Escopo analisado
- Todos os arquivos HTML em `libs/views/` e `libs/views/components/` que usam JS para injetar HTML/alterar classes.
- Arquivo `libs/views/static/js/status_usinas.js` (solicitado explicitamente).
- Verificação de redundâncias de funções/componentes.

## Resumo executivo
- Há **injeção de HTML via `innerHTML`/`insertAdjacentHTML`** principalmente em `libs/views/configuracoes.html` e nos componentes de RAT (`_criar_rats.html`, `_modificar_rats.html`, `_tabela_rats.html`).
- **Classes utilitárias (Tailwind) estão hardcoded nas strings JS**; mudar o nome das classes exige alterar o JS. Alterar apenas o CSS dessas classes ainda funciona.
- `libs/views/static/js/status_usinas.js` usa `<template>` (bom), mas ainda faz `innerHTML` e `className` com classes utilitárias.

## Arquivos com JS gerando HTML/classes

### `libs/views/configuracoes.html`
- **Onde ocorre**
  - `addUsina()` cria markup completo via template literal e injeta com `insertAdjacentHTML` (linhas ~151–233).
  - `addDispositivo()` cria markup completo via template literal e injeta com `insertAdjacentHTML` (linhas ~237–334).
  - `createEntradaSection()` retorna HTML de seção via template literal (linhas ~336–358).
  - `addCaracteristica()` injeta um bloco com classes via `insertAdjacentHTML` (linhas ~367–388).
  - `addEntrada()` injeta o bloco de entrada via `insertAdjacentHTML` (linhas ~390–463).
  - `removeEntrada()` e `limparTudo()` reescrevem `innerHTML` de containers (linhas ~477–486 e ~1192–1199).
  - `searchVariaveis()` monta cards de resultados via template literal e `insertAdjacentHTML` (linhas ~626–676), e mensagens vazias via `innerHTML` (linha ~682).
  - `testarLeitura()` e listener de socket usam `innerHTML` para status (linhas ~829–852 e ~1273–1294).
  - `showToast()` redefine classes via `className` com string (linha ~1178).
- **Impacto**
  - Mudanças de CSS que exigem renomear classes implicam alteração do JS.
  - HTML é “montado” no JS; qualquer ajuste estrutural no layout (ex. adicionar wrapper/div) precisa mudar o JS.

### `libs/views/components/_criar_rats.html`
- **Onde ocorre**
  - `selectObra.innerHTML = '<option ...>'` ao mudar cliente (linha ~375).
  - Reset/rehidratação de tabelas usando `innerHTML` (linhas ~485, ~527, ~550).
  - Autocomplete de produtos cria itens via `createElement` + `div.innerHTML` com classes (linhas ~780–792) e estados vazios via `innerHTML` (linha ~795).
  - Upload de foto troca o conteúdo de drop-area via `innerHTML` (linhas ~848–869).
  - `adicionarCardFoto()` monta card com classes via template literal e `div.innerHTML` (linhas ~878–891).
- **Impacto**
  - Classes dos cards, dos itens do autocomplete e do placeholder do drop-area estão hardcoded.

### `libs/views/components/_modificar_rats.html`
- **Onde ocorre**
  - Autocomplete de produtos repete o mesmo padrão de `_criar_rats.html` (linhas ~451–484).
  - Cards de foto são criados via `div.innerHTML` com classes (linhas ~520–533).
  - Limpeza de `resultsContainer.innerHTML` e controle de visibilidade (linhas ~426–431).
- **Impacto**
  - Mesma dependência de classes hardcoded do `_criar_rats.html`.

### `libs/views/components/_tabela_rats.html`
- **Onde ocorre**
  - Modal RAT: tabelas de serviços/materiais/fotos são montadas via `innerHTML` e `createElement` + `innerHTML` (linhas ~491–557).
  - Mensagens vazias usam `innerHTML` com classes (linhas ~508 e ~528).
  - Imagens/fotos com classes em template literal (linhas ~542–549).
  - `selectElement.className = ...` altera classes no status financeiro (linha ~600).
- **Impacto**
  - Classes de tabelas e cards do modal dependem de strings JS.

### `libs/views/components/_info_rats.html`
- **Onde ocorre**
  - `changePage()` faz fetch parcial e injeta HTML usando `tempDiv.innerHTML` (linhas ~155–175).
- **Impacto**
  - Dependência do markup retornado do backend para substituir `#rat-table-container`.

### `libs/views/components/_alert.html`
- **Onde ocorre**
  - `msgEl.innerHTML = message` permite HTML (linha ~45).
  - `className` aplicado com strings em múltiplos estados (linhas ~49–85).
- **Impacto**
  - Renomear classes do modal exige ajustes no JS.
  - Se o `message` vier de usuário, existe risco de XSS (depende da origem do texto).

### `libs/views/ocorrencias.html`
- **Onde ocorre**
  - `select.innerHTML = '<option ...>'` ao carregar ocorrências (linha ~565).
  - `el.className = ...` para toast (linha ~509).
- **Impacto**
  - Menor; mas ainda dependente de classes hardcoded.

### `libs/views/usinas.html`
- **Onde ocorre**
  - Criação dinâmica de badges de potência via `createElement` + `className` (linhas ~270–276).
- **Impacto**
  - Se classes dos badges mudarem, precisa ajustar o JS.

### `libs/views/static/js/status_usinas.js` (solicitado)
- **Onde ocorre**
  - Limpeza de containers via `innerHTML = ''` (linhas ~117 e ~124).
  - Mensagem “Sem dados” injetada via `innerHTML` com estilos inline (linha ~337).
  - `className = ...` para status dot, textos e barras (linhas ~318, ~321, ~324, ~381).
  - Badges de status e potência aplicam classes utilitárias via `className` (linhas ~425, ~444, ~458, ~468–476).
- **Observação positiva**
  - Uso de `<template>` para `template-card-temperatura`, `template-status-badge` e `template-potencia-badge` reduz o HTML em string.
- **Impacto**
  - Mudanças de nomenclatura de classes exigem ajustes aqui.
  - O trecho “Sem dados” usa estilo inline; não reage a mudanças no CSS global.

### `libs/views/js/status_usinas.js`
- Arquivo vazio (0 linhas). Não participa da renderização.

## Redundâncias e oportunidades de reutilização

1. **Autocomplete de produtos duplicado**
   - `libs/views/components/_criar_rats.html`: `buscarProduto()` + `selecionarProduto()` (linhas ~762–812).
   - `libs/views/components/_modificar_rats.html`: `buscarProduto()` + `selecionarProduto()` (linhas ~451–497).
   - **Risco**: ajustes futuros precisam ser replicados em dois lugares.

2. **Cards de foto** (padrões muito similares)
   - `_criar_rats.html` (linhas ~878–891) e `_modificar_rats.html` (linhas ~520–533) geram cards com estrutura e classes semelhantes.
   - **Risco**: divergência de UI e bugs em comportamentos.

3. **Mensagens de vazio**
   - Em `_tabela_rats.html` e `configuracoes.html` há placeholders com `innerHTML` para estados vazios.
   - **Risco**: estilo e texto inconsistentes entre telas.

4. **Toasts/alerts**
   - `configuracoes.html` possui `showToast()` (linhas ~1160–1189).
   - Componente global `customAlert` existe em `_alert.html`.
   - **Risco**: dois padrões de feedback visual diferentes.

## Conclusões
- **Sua percepção faz sentido**: quando as classes estão embutidas no JS, mudar o nome das classes no CSS **não surte efeito** até atualizar o JS.
- **Mudanças de estilo (sem renomear classes)** continuam funcionando, porque a classe ainda existe.
- `configuracoes.html` é o ponto mais crítico por montar grandes blocos de HTML no JS.

## Próximos passos sugeridos (sem alteração agora)
- Centralizar trechos repetidos em `<template>` HTML ou macros Jinja e reaproveitar no JS.
- Extrair utilitários comuns (ex.: autocomplete, criação de cards de foto, toasts) para um JS compartilhado.
- Substituir strings HTML por `template.cloneNode()` sempre que possível (reduz risco de inconsistência e facilita manutenção de CSS).
