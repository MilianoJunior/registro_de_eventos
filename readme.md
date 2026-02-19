# COG — Centro de Operação e Gestão de Usinas

> Sistema de supervisão, registro e gestão de eventos operacionais para Pequenas Centrais Hidrelétricas (PCH) e Centrais Geradoras Hidrelétricas (CGH), desenvolvido pela **Engesep**.

---

## 🎯 Propósito

Reduzir paradas e custo operacional em CGHs/PCHs transformando sinais e registros em ações padronizadas, notificações úteis e relatórios automáticos para o cliente.

**O software existe para transformar eventos em decisões:** menos paradas, mais energia faturada e relatórios automáticos — com uma rotina simples o suficiente para o operador querer usar.

---

## 🚀 Como Rodar

### Pré-requisitos
- Python 3.12+
- MySQL (ou acesso ao banco Railway)
- Ambiente virtual `amb`

### Instalação

```bash
# 1. Ativar o ambiente virtual
source /home/jrmfilho23/projetos/amb/bin/activate

# 2. Instalar dependências
pip install -r requeriments.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env   # editar com as credenciais reais

# 4. Iniciar o servidor
python main.py
```

O servidor sobe em `http://0.0.0.0:5001` por padrão.

---

## 🔑 Variáveis de Ambiente (`.env`)

| Variável | Descrição | Padrão |
|---|---|---|
| `MYSQLHOST` | Host do banco MySQL | — |
| `MYSQLUSER` | Usuário do banco | — |
| `MYSQLPASSWORD` | Senha do banco | — |
| `MYSQLDATABASE` | Nome do banco | — |
| `MYSQLPORT` | Porta do banco | `3306` |
| `MYSQLCONNECTIONTIMEOUT` | Timeout de conexão (s) | `10` |
| `MYSQL_POOL_SIZE` | Tamanho do pool de conexões | `10` |
| `SECRET_KEY` | Chave secreta do Flask (sessão) | `change-me` |
| `PORT` | Porta do servidor Flask | `5001` |
| `INTERVALO_COLETA` | Intervalo de coleta Modbus (s) | `30` |
| `DEV_RELOAD` | Ativa hot-reload de estáticos | `0` |
| `TEMP_DEBUG` | Ativa logs de depuração temporários | `0` |

---

## 📁 Estrutura do Projeto

```
registro_de_eventos/
├── main.py                        # Entrypoint Flask + SocketIO + thread de coleta
├── requeriments.txt               # Dependências Python
├── .env                           # Credenciais (não versionar)
├── config/
│   ├── usinas_dispositivos.json   # Configuração de usinas e dispositivos Modbus
│   └── intervencoes_operador.json # Intervenções manuais persistidas
├── assets/
│   └── clientes/                  # CSVs para seed de clientes
├── libs/
    ├── routes/
    │   └── routes.py              # Todas as rotas Flask (autenticação + páginas + API)
    ├── controllers/
    │   ├── homeController.py      # Dashboard principal
    │   ├── ocorrenciasController.py # Criação, listagem e resolução de ocorrências
    │   ├── usinasController.py    # Página individual por usina
    │   ├── ratsController.py      # CRUD completo de RATs + geração de PDF
    │   ├── configController.py    # Configurações das usinas
    │   └── decorador.py           # Decorator @desempenho (log de tempo)
    ├── models/
    │   ├── database.py            # Connection pool MySQL (singleton thread-safe)
    │   ├── read.py                # Classes Read por tabela (SELECT)
    │   ├── create.py              # Classes Create por tabela (INSERT)
    │   ├── edit.py                # Classes Edit por tabela (UPDATE)
    │   ├── delete.py              # Classes Delete por tabela (DELETE)
    │   ├── modelstate.py          # CacheStore + DadosContexto + ViewModels
    │   ├── rats_crud.py           # CRUD especializado para RATs
    │   └── docs/                  # Seeds e migrations (scripts pontuais)
    ├── servicos/
    │   ├── coletor_core.py        # Coleta async Modbus TCP de todas as usinas
    │   └── readRT.py              # Leitura individual de registradores Modbus
    ├── sockets/
    │   └── __init__.py            # Registro de handlers Socket.IO
    └── views/
        ├── base.html              # Layout base com sidebar, Socket.IO e tema dark/light
        ├── login.html             # Tela de login com rate-limit
        ├── home.html              # Dashboard com cards de usinas e KPIs
        ├── ocorrencias.html       # Registro e listagem de ocorrências
        ├── usinas.html            # Página individual por usina com timeline
        ├── rats.html              # RAT (Relatório de Assistência Técnica)
        ├── configuracoes.html     # Configuração de usinas e dispositivos
        ├── temperaturas.html      # Monitor de temperaturas em risco
        ├── error.html             # Página de erro genérico
        └── components/            # Componentes Jinja2 reutilizáveis
        |   ├── _cards.html
        |   ├── _info_rats.html
        |   ├── _criar_rats.html
        |   ├── _modificar_rats.html
        |   ├── _pdf_rats.html
        |   └── macros.html
        └── static/
            ├── css/
            │   ├── styles.css             # Design system (variáveis CSS globais)
            │   ├── card.css               # Estilos de cards
            │   └── tailwind.min.css       # Tailwind (offline)
            └── js/
                └── status_usinas.js       # Módulo de atualização de status via Socket.IO
```

---

## 🏗️ Arquitetura

### Fluxo Principal

```
Browser
  │
  ├─ HTTP → Flask routes.py → Controller → Model/DadosContexto → MySQL
  │
  └─ WebSocket (Socket.IO) ←── Thread Background (coletor_core.py → Modbus TCP)
                                      │
                                      └─ op_paradas (MySQL) ← persiste cada coleta
```

### Camadas

| Camada | Responsabilidade |
|---|---|
| **routes.py** | Autenticação, rate-limit, mapeamento URL → Controller |
| **Controllers** | Orquestra lógica de negócio, prepara ViewModel, chama Model |
| **DadosContexto** | Camada de dados com cache em memória (CacheStore + TTL) |
| **Models (Read/Create/Edit/Delete)** | Acesso direto ao MySQL via connection pool |
| **coletor_core.py** | Leitura async paralela das UGs via Modbus TCP a cada 30s |
| **Socket.IO** | Emite `status_usinas_dados` para todos os clientes em tempo real |

---

## 🔗 Rotas

### Autenticação

| Método | Rota | Descrição |
|---|---|---|
| `GET/POST` | `/login` | Tela e processamento de login (rate-limit: 5 tentativas / 5 min por IP) |
| `GET` | `/logout` | Encerra sessão |

### Páginas HTML

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Dashboard Home (cards de usinas + KPIs + temperaturas) |
| `GET` | `/usina/<sigla>` | Página individual da usina com timeline de ocorrências |
| `GET` | `/ocorrencias` | Registro e listagem de ocorrências |
| `GET` | `/rats` | Informações de RATs |
| `GET` | `/criarrat` | Formulário de criação de RAT |
| `GET` | `/modificarrat[/<rat_id>]` | Edição de RAT |
| `GET` | `/configuracoes` | Configuração das usinas |
| `GET` | `/temperaturas` | Monitor de temperaturas em risco |

### API JSON

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/salvar_ocorrencia` | Cria nova ocorrência |
| `GET` | `/listar_ocorrencias` | Lista ocorrências (filtros via querystring) |
| `PUT/POST` | `/resolver_ocorrencia/<id>` | Resolve uma ocorrência |
| `POST` | `/rat/salvar` | Cria RAT |
| `POST` | `/rat/atualizar` | Atualiza RAT existente |
| `POST` | `/rat/deletar` | Remove RAT e seus dados relacionados |
| `POST` | `/rat/upload_foto` | Upload de foto para o RAT |
| `GET` | `/rat/ver/<rat_id>` | Retorna dados completos do RAT |
| `GET` | `/rat/pdf/<rat_id>` | Gera PDF do RAT (preview ou download) |
| `POST` | `/rat/atualizar_status_financeiro` | Atualiza status financeiro do RAT |
| `GET` | `/produtos/buscar` | Busca produtos/materiais para RAT |
| `GET` | `/configuracoes/carregar` | Retorna configurações das usinas |
| `POST` | `/configuracoes/salvar` | Persiste configurações |

---

## 🗄️ Banco de Dados

### Connection Pool

- Pool singleton thread-safe (tamanho configurável via `MYSQL_POOL_SIZE`)
- Toda instância de `Database` obtém uma conexão do pool, usa e devolve no `finally`
- `autocommit=False` — commit explícito após cada operação de escrita

### Tabelas Principais

| Tabela | Descrição |
|---|---|
| `op_usina` | Cadastro das usinas monitoradas |
| `op_usuario` | Usuários e operadores |
| `op_ocorrencia` | Eventos operacionais registrados |
| `op_ocorrencia_hist` | Histórico/auditoria de mudanças nas ocorrências |
| `op_paradas` | Snapshots JSON de coleta Modbus (inserido a cada 30s) |
| `op_anexo` | Anexos e fotos de ocorrências |
| `clientes` | Clientes/usinas para faturamento (`nome_razao`, `cnpj`, `cidade`, `obras`) |
| `rats` | Relatórios de Assistência Técnica |
| `rat_servicos` | Serviços executados por RAT |
| `rat_materiais` | Materiais aplicados por RAT |
| `rat_fotos` | Fotos vinculadas ao RAT |

### Estrutura da Ocorrência

```sql
op_ocorrencia {
  id         BIGINT PK
  usina_id   BIGINT FK → op_usina
  tipo       VARCHAR   -- Evento | Alarme | Trip | Comando | Manutenção
  categoria  VARCHAR   -- Operação/Humano | Elétrica | Hidráulica | Mecânica | ...
  unidade    VARCHAR   -- UG-01 | Vertedouro | ...
  severidade ENUM      -- baixa | média | alta | crítica
  status     ENUM      -- aberta | em_andamento | resolvida | cancelada
  origem     ENUM      -- humano | scada | api | importacao
  descricao  LONGTEXT
  metadata   JSON
  created_at DATETIME
  resolved_at DATETIME
}
```

---

## ⚡ Coleta de Dados em Tempo Real (Modbus TCP)

### Fluxo de Coleta

1. **Thread background** (`coletor_background_thread`) inicia junto com o servidor
2. A cada `INTERVALO_COLETA` segundos (padrão: 30s), chama `coletar_status_completo()`
3. `coletor_core.py` lê `config/usinas_dispositivos.json` e dispara leituras **async paralelas** para cada dispositivo de cada usina
4. Para cada dispositivo UG, coleta via Modbus TCP:
   - **Status** (registradores BOOLEAN): US, UMD, UPS, UPGM, UP
   - **Potência Ativa** (MW)
   - **Temperaturas** (mancais, gaxeteiros, etc.)
   - **Níveis** (montante e jusante)
5. Resultado salvo em `op_paradas` (JSON) e emitido via `Socket.IO` (`status_usinas_dados`) para todos os clientes conectados

### Intervenções Manuais

Permitem sobrescrever o status de um dispositivo sem alterar a leitura Modbus:

- `MANUTENCAO` → exibe "Manutenção (parada)"
- `RESTRICAO` → exibe "Restrição da concessionária (parada)"
- `NORMAL` → remove o override

Intervenções são persistidas em `config/intervencoes_operador.json` (sobrevivem a restarts).

---

## 🧠 Cache em Memória

### CacheStore

Cache global com TTL por chave. Registra `MISS / HIT / EXPIRED / SET / DEL` no console com prefixo `[CACHE]`.

### TTLs Configurados

| Chave | TTL | Dado |
|---|---|---|
| `usinas` | 6h | Cadastro de usinas |
| `usuarios` | 6h | Lista de usuários |
| `ocorrencias_N` | 6h* | Ocorrências recentes (atualização incremental por ID) |
| `stats_status` | 5min | Contagem de ocorrências por status |
| `kpis_mttr` | 5min | MTTR por usina |
| `temperaturas` | 1min | Temperaturas em risco |
| `ocorrencias_requer_acao` | 30s | Ocorrências com ação pendente |

\* Atualização incremental a cada 60s: busca apenas registros com ID > último ID em cache, sem recarregar tudo.

---

## 📝 Fluxo Operacional (Ocorrência → RAT)

```
1. Operador detecta evento na usina
       ↓
2. Registra ocorrência em /ocorrencias
       ↓
3. Se "requer ação urgente" → entra na fila de ações pendentes
       ↓
4. Equipe resolve operacionalmente → registra resolução
       ↓
5. Equipe vai a campo → conclui ação física
       ↓
6. Cria RAT em /criarrat com:
   - Serviços executados (horas de início/fim por dia)
   - Materiais aplicados
   - Fotos de evidência
   - Assinaturas (técnico + cliente)
       ↓
7. Gera PDF do RAT em /rat/pdf/<id>
```

---

## 🧾 RAT (Relatório de Assistência Técnica)

- Criação, edição e exclusão de RATs com relacionamentos em cascata
- Upload de fotos associadas ao RAT
- Cálculo automático de horas trabalhadas por serviço
- Geração de PDF via **WeasyPrint** (template HTML → PDF renderizado)
- Status financeiro atualizável independentemente

---

## 🔒 Autenticação

- Usuários definidos em memória no `routes.py` (sem banco de dados)
- Login por username ou e-mail + senha
- Sessão Flask com `session.permanent` para "lembrar-me"
- Rate-limit em memória: **5 tentativas por IP a cada 5 minutos**
- Todas as rotas exigem sessão ativa, exceto `/login`, `/static/` e `/socket.io/`

---

## 🎨 Design System

- **Framework CSS**: Tailwind (offline) + variáveis globais em `styles.css`
- **Tema**: dark/light mode com toggle persistido em `localStorage`
- **Componentes**: reutilizados via Jinja2 `{% include %}` e `{% macro %}`
- **Nenhum HTML em strings JS** — usar `<template>` para clones dinâmicos

---

## 🛠️ Dependências

| Pacote | Versão | Uso |
|---|---|---|
| `Flask` | 3.0.0 | Framework web |
| `Flask-SocketIO` | 5.3.5 | WebSocket (Socket.IO) |
| `mysql-connector-python` | 8.2.0 | Driver MySQL com pool |
| `python-dotenv` | 1.0.0 | Variáveis de ambiente |
| `python-socketio` | 5.10.0 | Backend Socket.IO |
| `eventlet` | 0.33.3 | Async mode Socket.IO |
| `watchdog` | 3.0.0 | Hot-reload de estáticos (DEV) |
| `WeasyPrint` | latest | Geração de PDF |
| `werkzeug` | latest | Utilitários HTTP/HTTP |
| `httpx` | latest | Requisições HTTP async |
| `python-dateutil` | 2.8.2 | Parsing de datas |

---

## 📚 Documentação Adicional

- **[`.agent/rules/projeto.md`](.agent/rules/projeto.md)** — Regras de arquitetura e convenções de código para o agente de IA
- **[`config/usinas_dispositivos.json`](config/usinas_dispositivos.json)** — Configuração de usinas, IPs, portas e registradores Modbus
- **[`libs/models/docs/`](libs/models/docs/)** — Seeds e scripts de migração do banco de dados
