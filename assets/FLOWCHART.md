# 🔄 Fluxograma do Projeto - Sistema COG (Monitoramento de Usinas)

## 📊 Visão Geral da Arquitetura

```mermaid
graph TB
    subgraph "Frontend - Interface do Usuário"
        A[📱 Navegador Web] --> B[🏠 Home Page]
        A --> C[⚡ Página Usina Individual]
        B --> D[📊 Cards de Status]
        B --> E[🚨 Registro de Ocorrências]
        C --> F[📈 Gráficos Detalhados]
        C --> G[🔍 Informações da Usina]
    end

    subgraph "Backend - Aplicação Flask"
        H[🌐 main.py - Flask App] --> I[🛤️ Routes]
        I --> J[🎮 homeController]
        I --> K[🎮 usinasController]
        J --> L[📖 Read Models]
        K --> L
        L --> M[💾 Database Singleton]
        H --> N[🔌 SocketIO - WebSocket]
        H --> O[👀 File Watcher]
    end

    subgraph "Camada de Dados"
        M --> P[(🗄️ MySQL Database)]
        P --> Q[📋 op_usina]
        P --> R[📋 op_ocorrencia]
        P --> S[📋 op_usuario]
        P --> T[📋 op_ug - Unidades Geradoras]
    end

    subgraph "Sistema de Design"
        U[🎨 variables.css] --> V[📦 Componentes]
        V --> W[🃏 Cards]
        V --> X[🔘 Buttons]
        V --> Y[📝 Inputs]
        V --> Z[🏷️ Chips]
    end

    A --> H
    L --> B
    L --> C
    U --> B
    U --> C
    N -.-> |Updates em tempo real| A
    O -.-> |Hot reload| A

    style A fill:#3b82f6,stroke:#1e40af,color:#fff
    style H fill:#22c55e,stroke:#16a34a,color:#fff
    style P fill:#ef4444,stroke:#dc2626,color:#fff
    style U fill:#eab308,stroke:#ca8a04,color:#000
```

## 🔄 Fluxo de Requisição HTTP

```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant B as 🌐 Browser
    participant F as ⚙️ Flask App
    participant R as 🛤️ Routes
    participant C as 🎮 Controller
    participant M as 📖 Models
    participant DB as 💾 Database
    participant T as 📄 Template

    U->>B: Acessa URL
    B->>F: HTTP Request
    F->>R: Roteamento
    R->>C: Chama Controller
    C->>M: Solicita dados
    M->>DB: Query SQL
    DB-->>M: Retorna dados
    M-->>C: Dados processados
    C->>T: Renderiza com dados
    T-->>F: HTML gerado
    F-->>B: HTTP Response
    B-->>U: Página renderizada
```

## 📁 Estrutura do Projeto

```mermaid
graph LR
    A[📂 Workspace] --> B[🐍 main.py]
    A --> C[📂 libs]
    A --> D[📂 testes]
    A --> E[📂 assets]
    
    C --> F[📂 controllers]
    C --> G[📂 models]
    C --> H[📂 routes]
    C --> I[📂 views]
    
    F --> F1[homeController.py]
    F --> F2[usinasController.py]
    
    G --> G1[database.py - Singleton]
    G --> G2[read.py - CRUD]
    G --> G3[edit.py - Updates]
    G --> G4[📂 utils]
    
    H --> H1[routes.py]
    
    I --> I1[📄 Templates HTML]
    I --> I2[📂 static CSS/JS]
    I --> I3[📂 components]
    
    D --> D1[test_read_models.py]
    D --> D2[test_edit_models.py]

    style A fill:#0f172a,stroke:#3b82f6,color:#fff
    style C fill:#1f2937,stroke:#22c55e,color:#fff
    style G1 fill:#ef4444,stroke:#dc2626,color:#fff
```

## 🎯 Fluxo de Dados - Home Page

```mermaid
graph TD
    A[🏠 Rota: /] --> B[homeController.home]
    B --> C{Cache existe?}
    C -->|Sim| D[Retorna dados em cache]
    C -->|Não| E[Read - op_usina]
    C -->|Não| F[Read - op_ocorrencia]
    
    E --> G[get_all usinas]
    F --> H[get_all ocorrencias limit 20]
    
    G --> I[💾 Cache]
    H --> I
    
    I --> J[Processa dados]
    J --> K[Ordena recentes top 10]
    J --> L[Conta por status]
    J --> M[Conta por unidade top 8]
    
    K --> N[render_template home.html]
    L --> N
    M --> N
    
    N --> O[📊 Página renderizada]
    O --> P[Cards de Usinas]
    O --> Q[Status das Ocorrências]
    O --> R[Registro de Incidentes]

    style B fill:#22c55e,stroke:#16a34a,color:#fff
    style I fill:#eab308,stroke:#ca8a04,color:#000
    style O fill:#3b82f6,stroke:#1e40af,color:#fff
```

## 🔌 Sistema de Conexão com Banco de Dados

```mermaid
stateDiagram-v2
    [*] --> Desconectado
    Desconectado --> Tentando_Conectar: connect()
    Tentando_Conectar --> Conectado: Sucesso
    Tentando_Conectar --> Erro: Falha
    Conectado --> Executando: execute_query()
    Executando --> Conectado: Sucesso + Commit
    Executando --> Rollback: Erro
    Rollback --> Conectado: Retry
    Conectado --> Verificando: _is_alive()
    Verificando --> Conectado: Conexão OK
    Verificando --> Reconectando: Conexão perdida (2006, 2013, 2055)
    Reconectando --> Conectado: Reconexão OK (retry automático)
    Reconectando --> Erro: Falha após 3 tentativas
    Erro --> [*]
    Conectado --> Desconectado: close()
```

## 📋 Modelo de Dados - Ocorrências

```mermaid
erDiagram
    OP_OCORRENCIA {
        bigint id PK
        bigint usina_id FK
        bigint ug_id FK
        bigint operador_id FK
        enum origem
        enum tipo
        int categoria_id
        enum prioridade
        varchar titulo
        text descricao
        varchar tag
        decimal valor
        varchar unidade_medida
        datetime ts_inicio
        datetime ts_fim
        enum estado
    }
    
    OP_USINA {
        bigint id PK
        varchar nome
        varchar sigla
        boolean ativo
        datetime created_at
    }
    
    OP_USUARIO {
        bigint id PK
        varchar nome
        varchar email
        enum perfil
        boolean ativo
    }
    
    OP_UG {
        bigint id PK
        bigint usina_id FK
        varchar nome
        decimal potencia_nominal
    }
    
    OP_OCORRENCIA ||--o{ OP_USINA : "pertence a"
    OP_OCORRENCIA ||--o{ OP_UG : "relacionada a"
    OP_OCORRENCIA ||--o{ OP_USUARIO : "registrada por"
    OP_UG ||--o{ OP_USINA : "faz parte de"
```

## 🎨 Sistema de Componentes UI

```mermaid
graph TB
    A[🎨 variables.css] --> B[Tema Global]
    B --> C[Cores]
    B --> D[Espaçamentos]
    B --> E[Tipografia]
    B --> F[Bordas e Raios]
    
    C --> G[components.css]
    D --> G
    E --> G
    F --> G
    
    G --> H[📦 Componentes Reutilizáveis]
    
    H --> I[🃏 Cards]
    H --> J[🔘 Buttons]
    H --> K[📝 Inputs]
    H --> L[🏷️ Chips]
    H --> M[📊 Tables]
    
    I --> N[home.html]
    I --> O[usinas.html]
    J --> N
    J --> O
    K --> N
    L --> N
    M --> N

    style A fill:#eab308,stroke:#ca8a04,color:#000
    style G fill:#22c55e,stroke:#16a34a,color:#fff
    style H fill:#3b82f6,stroke:#1e40af,color:#fff
```

## 🚀 Status Atual e Roadmap

```mermaid
graph LR
    subgraph "✅ Implementado - MVP"
        A1[🏠 Home Page]
        A2[📊 Dashboard Usinas]
        A3[💾 Database Singleton]
        A4[📖 Sistema Read CRUD]
        A5[🎨 Design System]
        A6[🔌 WebSocket Setup]
        A7[⚡ Página Usina Individual]
    end
    
    subgraph "🚧 Em Desenvolvimento"
        B1[📝 Registro Manual de Eventos]
        B2[📈 Gráficos Detalhados]
        B3[🔔 Sistema de Notificações]
        B4[🎯 Priorização de Eventos]
    end
    
    subgraph "📅 Próximos Passos"
        C1[🔧 Página de Configurações]
        C2[📊 KPIs por UG]
        C3[🌡️ Monitoramento Temperaturas]
        C4[📈 Geração de Relatórios]
        C5[🔄 Sistema de ACK]
        C6[👥 Gestão de Usuários]
        C7[📱 Responsividade Mobile]
    end
    
    subgraph "🎯 Futuro"
        D1[🤖 IA - Predição de Falhas]
        D2[📧 Notificações Email/SMS]
        D3[📊 Analytics Avançado]
        D4[🔐 Autenticação OAuth]
        D5[📦 API REST Pública]
    end
    
    A1 --> B1
    A2 --> B2
    A7 --> B2
    B1 --> C1
    B2 --> C2
    B4 --> C3
    C4 --> D1
    C6 --> D4

    style A1 fill:#22c55e,stroke:#16a34a,color:#fff
    style A2 fill:#22c55e,stroke:#16a34a,color:#fff
    style A3 fill:#22c55e,stroke:#16a34a,color:#fff
    style A4 fill:#22c55e,stroke:#16a34a,color:#fff
    style A5 fill:#22c55e,stroke:#16a34a,color:#fff
    style A6 fill:#22c55e,stroke:#16a34a,color:#fff
    style A7 fill:#22c55e,stroke:#16a34a,color:#fff
    
    style B1 fill:#eab308,stroke:#ca8a04,color:#000
    style B2 fill:#eab308,stroke:#ca8a04,color:#000
    style B3 fill:#eab308,stroke:#ca8a04,color:#000
    style B4 fill:#eab308,stroke:#ca8a04,color:#000
    
    style C1 fill:#3b82f6,stroke:#1e40af,color:#fff
    style C2 fill:#3b82f6,stroke:#1e40af,color:#fff
    style C3 fill:#3b82f6,stroke:#1e40af,color:#fff
    style C4 fill:#3b82f6,stroke:#1e40af,color:#fff
    style C5 fill:#3b82f6,stroke:#1e40af,color:#fff
    style C6 fill:#3b82f6,stroke:#1e40af,color:#fff
    style C7 fill:#3b82f6,stroke:#1e40af,color:#fff
```

## 🔄 Ciclo de Desenvolvimento

```mermaid
graph TB
    A[📝 Requisito] --> B[💡 Planejamento]
    B --> C[👨‍💻 Implementação]
    C --> D[🧪 Testes]
    D --> E{Passou nos testes?}
    E -->|Sim| F[📦 Deploy MVP]
    E -->|Não| C
    F --> G[📊 Coleta Feedback]
    G --> H{Precisa melhorar?}
    H -->|Sim| I[🔄 Iteração]
    H -->|Não| J[✅ Feature Completa]
    I --> B
    J --> K[📈 Próxima Feature]
    K --> A

    style F fill:#22c55e,stroke:#16a34a,color:#fff
    style J fill:#3b82f6,stroke:#1e40af,color:#fff
    style E fill:#eab308,stroke:#ca8a04,color:#000
```

## 📊 Principais Integrações

```mermaid
graph TD
    A[Sistema COG] --> B[SCADA]
    A --> C[CLP]
    A --> D[API Externa]
    A --> E[Sensores]
    A --> F[Transformador]
    A --> G[CELESC]
    
    B -.->|Eventos| H[op_ocorrencia]
    C -.->|Alarmes| H
    D -.->|Comandos| H
    E -.->|Leituras| H
    F -.->|Status| H
    G -.->|Dados| H
    
    H --> I[Processamento]
    I --> J[Dashboard]
    I --> K[Notificações]
    I --> L[Relatórios]

    style A fill:#3b82f6,stroke:#1e40af,color:#fff
    style H fill:#ef4444,stroke:#dc2626,color:#fff
    style I fill:#22c55e,stroke:#16a34a,color:#fff
```

---

## 📌 Legenda

- 🏠 **Home**: Página principal com visão geral
- ⚡ **Usina**: Página detalhada por usina
- 📊 **Dashboard**: Visualização de métricas
- 🚨 **Ocorrências**: Sistema de eventos e alarmes
- 💾 **Database**: Camada de dados
- 🎨 **Design System**: Sistema de componentes UI
- 🔌 **WebSocket**: Comunicação em tempo real
- ✅ **Implementado**: Features completas
- 🚧 **Em Desenvolvimento**: Work in progress
- 📅 **Próximos Passos**: Backlog priorizado
- 🎯 **Futuro**: Roadmap de longo prazo

---

## 🎯 Propósito do Sistema

**Reduzir paradas e custo operacional em CGHs/PCHs** transformando sinais e registros em:
- ✅ Ações padronizadas
- 🔔 Notificações úteis
- 📊 Relatórios automáticos

**Objetivo**: Menos paradas, mais energia faturada e relatórios automáticos — com uma rotina tão simples que o operador quer usar.

