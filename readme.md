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

### 📝 Página - Novo Evento

**Descrição:** Registro do novo evento.

### ⚡ Página - Usinas

**Descrição:** Página personalizada para cada op_usina, com gráficos e informações mais detalhadas.

### ⚙️ Página - Configurações

**Descrição:** Página para configurar as variáveis que alteram o desempenho do COG.

---

## 📊 Estrutura de Eventos

Os Eventos devem conter as seguintes colunas:

```sql
id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
usina_id            BIGINT NOT NULL,
ug_id               BIGINT NULL,
operador_id         BIGINT NULL,  -- quem registrou/ack
origem              ENUM('SCADA','CLP','API','MANUAL','SENSOR','TRANSFORMADOR','CELESC') NOT NULL,
tipo                ENUM('evento','alarme','comando') NOT NULL,
categoria_id        INT NOT NULL,
prioridade          ENUM('baixa','media','alta') NOT NULL,
titulo              VARCHAR(160) NOT NULL,
descricao           TEXT,
tag                 VARCHAR(120),
valor               DECIMAL(18,6) NULL,
unidade_medida      VARCHAR(16),
ts_inicio           DATETIME(6) NOT NULL,
ts_fim              DATETIME(6) NULL,
estado              ENUM('novo','ativo','reconhecido','investigando','resolvido','cancelado') NOT NULL DEFAULT 'novo'
```

---

## 🚀 MVP - Status Atual

Nesse primeiro momento, vamos fazer apenas a página Home. A partir do projeto em anexo, os dados de leitura do tempo real já estão sendo realizadas corretamente.

**Abordagem MVP:**
- Vamos considerar isso como um MVP
- Não vamos inserir muita complexidade inicialmente
- Não vamos alterar a lógica de leitura existente
- O registro manual de eventos será implementado posteriormente

---

## 📚 Documentação Adicional

Para mais detalhes sobre a arquitetura e fluxogramas do sistema, consulte:
- [FLOWCHART.md](./FLOWCHART.md) - Fluxogramas detalhados do projeto
- [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) - Sistema de design e componentes UI
