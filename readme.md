# Sistema COG - Monitoramento de Usinas

## 🎯 Propósito

Reduzir paradas e custo operacional em CGHs/PCHs transformando sinais e registros em ações padronizadas, notificações úteis e relatórios automáticos para o cliente.

**Nosso software existe para transformar eventos em decisões e resultados:** menos paradas, mais energia faturada e relatórios automáticos — com uma rotina tão simples que o operador quer usar.

---

## 📋 Requisitos

### Funcionalidades Principais (com poucos cliks)

- O operador deve registrar um novo evento
- O gerenciador deve saber os principais eventos em todas as usinas monitoradas
- O sistema deve priorizar os eventos que podem ser mais críticos, seguindo uma classificação

---

## 📄 Páginas do Sistema

### 🏠 Página - Home

**Descrição:** Página principal que mostra uma visão geral e contém no máximo 6 usinas, divididas em 2 linhas e 3 colunas de forma responsiva. Será feito um roteamento dessa página home para mostrar mais usinas em outras páginas pelo navegador.

#### KPI - Key Performance Indicator (Indicador chave de desempenho)

Para cada `op_usina` e cada Unidade Geradora (UG):

- Indicador se a UG está parada ou operacional e botão que leva à tela personalizada da op_usina com mais informações
- Quanto cada UG gerou de potência - geração instantânea, dia, mês
- Nível montante (valor comum entre as UG's) e jusante (valor individual para cada UG) - instantânea, taxa de variação (mma 12 min), dia, mês e diferencial de grade (nível montante - nível jusante)
- Temperaturas de todas as usinas, ordenadas pelo valor do maior risco, com valores de alarme e trip, onde o risco é calculado pela razão entre o valor atual e o TRIP
- Display de eventos para cada UG e botão para inserir manualmente um novo evento, com cores definidas para as prioridades dos eventos

### 📝 Página - Registro de Eventos

**Descrição:** Página para registro e gerenciamento de ocorrências operacionais, permitindo criar novos eventos, visualizar histórico, adicionar anexos e acompanhar o status das ocorrências.

### 📊 Página - Análise e Relatórios

**Descrição:** Página para visualização de análises, métricas e relatórios consolidados das usinas e ocorrências.

### ⚡ Página - Usinas

**Descrição:** Página personalizada para cada op_usina, com gráficos e informações mais detalhadas.

### ⚙️ Página - Configurações

**Descrição:** Página para configurar as variáveis que alteram o desempenho do COG.

---

## 🏗️ Arquitetura do Projeto

O sistema segue uma arquitetura MVC (Model-View-Controller) organizada da seguinte forma:

### Estrutura de Diretórios

```
10_registro_eventos/
├── libs/
│   ├── controllers/      # Controladores de lógica de negócio
│   │   ├── homeController.py
│   │   ├── eventosController.py
│   │   ├── usinasController.py
│   │   └── analiseController.py
│   ├── models/          # Camada de acesso ao banco de dados
│   │   ├── read.py      # Classes para operações SELECT
│   │   ├── edit.py      # Classes para operações UPDATE
│   │   ├── create.py    # Classes para operações INSERT
│   │   ├── delete.py    # Classes para operações DELETE
│   │   ├── database.py  # Gerenciamento de conexões
│   │   └── docs/        # Documentação do banco
│   ├── routes/          # Definição de rotas Flask
│   │   └── routes.py
│   └── views/           # Templates HTML e arquivos estáticos
│       ├── home.html
│       ├── registro_eventos.html
│       ├── usinas.html
│       ├── analise_relatorios.html
│       ├── components/  # Componentes reutilizáveis
│       └── static/      # CSS, imagens, JS
├── main.py              # Ponto de entrada da aplicação Flask
└── requeriments.txt     # Dependências Python
```

### Camadas da Aplicação

1. **Views (Apresentação):** Templates HTML com Jinja2
2. **Controllers (Lógica):** Processamento de requisições e orquestração
3. **Models (Dados):** Classes abstratas para acesso ao banco de dados MySQL

---

## 📊 Estrutura de Ocorrências

O sistema utiliza a tabela `op_ocorrencia` para registrar eventos operacionais:

```sql
-- Tabela principal de ocorrências
op_ocorrencia {
  BIGINT id PK                    -- Identificador único
  BIGINT usina_id FK              -- Usina relacionada
  BIGINT operador_id FK           -- Operador que registrou
  VARCHAR tipo                    -- Ex.: Evento, Alarme, Trip
  VARCHAR categoria               -- Ex.: Operação/Humano, Elétrica, Hidráulica
  VARCHAR unidade                 -- Ex.: UG-01, Vertedouro
  VARCHAR tags                    -- Tags em formato CSV
  TEXT playbook                   -- Instruções de resposta
  TEXT template_texto             -- Template aplicado
  LONGTEXT descricao              -- Descrição detalhada
  ENUM status                     -- aberta|em_andamento|resolvida|cancelada
  ENUM severidade                 -- baixa|média|alta|crítica
  ENUM origem                     -- humano|scada|api|importacao
  JSON metadata                   -- Dados extras de integração
  DATETIME created_at
  DATETIME updated_at
  DATETIME resolved_at            -- Data de resolução (nullable)
}
```

### Estrutura do Banco de Dados

O sistema é composto por 5 tabelas principais:

1. **`op_usina`** - Cadastro de usinas
2. **`op_usuario`** - Usuários e operadores do sistema
3. **`op_ocorrencia`** - Registro de eventos operacionais
4. **`op_ocorrencia_hist`** - Histórico e auditoria de mudanças
5. **`op_anexo`** - Anexos de evidências (fotos, relatórios, etc.)

#### Relacionamentos:
- Uma usina possui muitas ocorrências (1:N)
- Um operador registra muitas ocorrências (1:N)
- Uma ocorrência possui histórico de auditoria (1:N)
- Uma ocorrência pode ter múltiplos anexos (1:N)

Para detalhes completos sobre a estrutura do banco, métodos de consulta e operações, consulte:
- [📘 Documentação do Banco de Dados](./libs/models/docs/database.md) - Schema completo, modelos e API de acesso

---

## 📚 Documentação Adicional

Para mais detalhes sobre a arquitetura e componentes do sistema:

- **[📘 Database Documentation](./libs/models/docs/database.md)** - Documentação completa do banco de dados
  - Schema de todas as tabelas
  - API de leitura (`Read`) - métodos como `get_all()`, `where()`, `get_by_id()`, etc.
  - API de edição (`Edit`) - métodos como `update_by_id()`, `update_where()`, `increment()`, etc.
  - Operadores de filtro e consultas avançadas
  - Diagramas ER (Entity-Relationship)

- **[🔄 FLOWCHART.md](./FLOWCHART.md)** - Fluxogramas detalhados do projeto

- **[🎨 DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)** - Sistema de design e componentes UI
