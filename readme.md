# COG — Centro de Operação e Gestão de Usinas

> Sistema web da Engesep para acompanhamento operacional de usinas, registro de ocorrências, configuração de leituras remotas e gestão de RATs.

---

## Propósito

O COG centraliza, em uma única aplicação, quatro frentes que hoje convivem no mesmo fluxo operacional:

- acompanhamento do status das usinas e dispositivos em tempo real;
- registro e resolução de ocorrências operacionais;
- configuração das leituras remotas por usina/dispositivo;
- criação, edição, consulta e exportação de RATs.

Na prática, o sistema combina dados vindos do MySQL, arquivos JSON de configuração e uma coleta contínua publicada via Socket.IO para alimentar dashboard, monitoramento, telas por usina e monitor de temperaturas.

---

## O que o sistema faz hoje

- Exibe na home o status operacional das usinas, potência por dispositivo, ocorrências recentes e temperaturas com maior risco.
- Mantém uma tela de monitoramento em tempo real (`/monitoramento`) com cards das usinas.
- Permite registrar ocorrências manuais, marcar se requerem ação urgente e concluir a resolução depois.
- Exibe uma página por usina com timeline filtrável de ocorrências e atualização em tempo real da potência por dispositivo.
- Permite configurar usinas e dispositivos em `config/usinas_dispositivos.json` pela interface web.
- Testa leituras individuais de variáveis via Socket.IO na tela de configuração.
- Gera e mantém RATs com serviços, materiais, fotos, assinaturas, deslocamento e status financeiro.
- Gera PDF de RAT com WeasyPrint.
- Permite geração assistida por IA para texto de descrição/conclusão do RAT quando `GEMINI_API_KEY` está configurada.

---

## Stack real usada

| Camada | Tecnologias em uso no código |
| --- | --- |
| Backend web | Flask 3.0.0 |
| Tempo real | Flask-SocketIO 5.3.5 com `async_mode="threading"` |
| Templates | Jinja2 |
| Front-end | Tailwind CSS local, CSS próprio, Alpine.js via CDN, Socket.IO client via CDN |
| Banco | MySQL via `mysql-connector-python` com connection pool |
| Coleta remota | `httpx` chamando uma API HTTP externa de leitura (`/readCLP/leituras`, `/listConnections`, `/closeConnections`) |
| PDF | WeasyPrint |
| Uploads | Werkzeug |
| Reload de arquivos | watchdog |
| Variáveis de ambiente | python-dotenv |
| Geração assistida por IA | `google.generativeai` (Gemini) |

### Observações importantes do estado atual

- O projeto instala `eventlet`, mas a inicialização atual do Socket.IO usa `threading`.
- O código importa `google.generativeai` no carregamento dos sockets; por isso, a dependência `google-generativeai` precisa estar instalada mesmo para subir a aplicação como ela está hoje.
- A coleta remota não fala Modbus diretamente no processo Flask: ela envia requisições HTTP para um serviço externo que executa as leituras.
- `python-dotenv` é carregado em `libs/models/database.py`; como `main.py` lê `SECRET_KEY` e faz a primeira leitura de `DEV_RELOAD` antes disso, essas duas variáveis não dependem apenas do `.env` no estado atual da inicialização.
- O `main.py` lê `DEV_RELOAD` no início, mas depois sobrescreve `DEV_RELOAD = True`; no estado atual do código, o watcher de arquivos fica sempre ativo.

---

## Como executar

### Pré-requisitos

- Python 3 com `venv`
- MySQL com as tabelas usadas pelo projeto
- Serviço HTTP de leitura dos CLPs acessível nos IPs e portas definidos em `config/usinas_dispositivos.json`

### Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requeriments.txt
pip install google-generativeai
```

### Configuração do ambiente

Crie ou ajuste o arquivo `.env` na raiz do projeto com as variáveis listadas na próxima seção.

### Execução

```bash
python main.py
```

Por padrão, a aplicação sobe em `http://127.0.0.1:5001` e escuta em `0.0.0.0:5001`.

### Observações de execução

- O arquivo de dependências versionado é `requeriments.txt`.
- Não existe `.env.example` versionado no repositório.
- O watcher do `watchdog` fica ativo no estado atual do `main.py` e emite `file_changed` para alterações em `.html`, `.css` e `.js`.
- Existe modo mock em `libs/models/utils/mock_data.py`, mas ele é controlado por constante em código (`DEVELOPER_MODE`) e está `False` no repositório.
- Se você precisar trocar `SECRET_KEY`, prefira exportar a variável no ambiente do processo, porque ela é lida antes do `load_dotenv()` atual.

---

## Variáveis de ambiente (`.env`)

| Variável | Uso no código | Padrão |
| --- | --- | --- |
| `MYSQLHOST` | Host do MySQL | — |
| `MYSQLUSER` | Usuário do MySQL | — |
| `MYSQLPASSWORD` | Senha do MySQL | — |
| `MYSQLDATABASE` | Banco de dados | — |
| `MYSQLPORT` | Porta do MySQL | `3306` |
| `MYSQLCONNECTIONTIMEOUT` | Timeout de conexão do MySQL | `10` |
| `MYSQL_POOL_SIZE` | Tamanho do pool de conexões | `10` |
| `SECRET_KEY` | Chave de sessão do Flask; lida antes do `load_dotenv()` atual | `change-me` |
| `PORT` | Porta HTTP da aplicação | `5001` |
| `INTERVALO_COLETA` | Intervalo da thread de coleta em segundos | `30` |
| `TEMP_DEBUG` | Logs extras de debug para coleta/inserção/temperaturas | `0` |
| `LOGS` | Nível do decorador de desempenho (`0`, `1` ou `2`) | `1` |
| `GEMINI_API_KEY` | Chave usada no socket `gerar_relatorio_ia` | — |
| `DEV_RELOAD` | Lida no início do `main.py`, mas atualmente ignorada na prática porque o arquivo força `DEV_RELOAD = True` | `0` |

Exemplo mínimo:

```env
MYSQLHOST=127.0.0.1
MYSQLPORT=3306
MYSQLUSER=seu_usuario
MYSQLPASSWORD=sua_senha
MYSQLDATABASE=cog
MYSQLCONNECTIONTIMEOUT=10
MYSQL_POOL_SIZE=10
SECRET_KEY=troque-esta-chave
PORT=5001
INTERVALO_COLETA=30
TEMP_DEBUG=0
LOGS=1
GEMINI_API_KEY=
```

---

## Estrutura do projeto

```text
registro_de_eventos/
├── main.py
├── readme.md
├── requeriments.txt
├── assets/
│   ├── logo.png
│   ├── logo.webp
│   ├── RAT/
│   │   ├── imgs/
│   │   └── signatures/
│   └── *.md
├── config/
│   ├── README.md
│   ├── usinas_dispositivos.json
│   └── intervencoes_operador.json   # criado/atualizado quando há override manual
├── libs/
│   ├── controllers/
│   │   ├── configController.py
│   │   ├── decorador.py
│   │   ├── homeController.py
│   │   ├── ocorrenciasController.py
│   │   ├── ratsController.py
│   │   └── usinasController.py
│   ├── models/
│   │   ├── create.py
│   │   ├── database.py
│   │   ├── delete.py
│   │   ├── edit.py
│   │   ├── modelstate.py
│   │   ├── rats_crud.py
│   │   ├── read.py
│   │   ├── utils/
│   │   └── docs/
│   ├── routes/
│   │   └── routes.py
│   ├── servicos/
│   │   ├── coletor_core.py
│   │   ├── mttr_tracker.py
│   │   └── readRT.py
│   ├── sockets/
│   │   ├── __init__.py
│   │   ├── ai_generation.py
│   │   ├── status_usina.py
│   │   └── testar_leitura.py
│   └── views/
│       ├── base.html
│       ├── configuracoes.html
│       ├── error.html
│       ├── home.html
│       ├── login.html
│       ├── monitoramento.html
│       ├── ocorrencias.html
│       ├── rats.html
│       ├── temperaturas.html
│       ├── usinas.html
│       ├── components/
│       └── static/
└── testes/
```

---

## Módulos principais

| Módulo | Papel atual |
| --- | --- |
| `main.py` | Inicializa Flask, Socket.IO, filtros Jinja, error handlers, watcher de arquivos e thread de coleta |
| `libs/routes/routes.py` | Define autenticação, proteção de rotas, páginas HTML e endpoints JSON |
| `libs/controllers/homeController.py` | Monta a home e a tela de monitoramento |
| `libs/controllers/usinasController.py` | Monta a página individual de usina com timeline filtrável |
| `libs/controllers/ocorrenciasController.py` | Cria, lista e resolve ocorrências |
| `libs/controllers/configController.py` | Carrega/salva o JSON de usinas e dispositivos |
| `libs/controllers/ratsController.py` | Lista, cria, edita, exclui, exporta PDF e consulta RATs |
| `libs/models/modelstate.py` | Centraliza leitura dos dados com cache em memória e view models |
| `libs/models/read.py` | Leituras do MySQL, incluindo extração de temperaturas a partir de `op_paradas` |
| `libs/models/rats_crud.py` | CRUD especializado e KPIs do módulo de RAT |
| `libs/servicos/coletor_core.py` | Orquestra a coleta contínua, aplica overrides e monta o payload em tempo real |
| `libs/servicos/readRT.py` | Cliente HTTP assíncrono para a API externa de leitura dos CLPs |
| `libs/servicos/mttr_tracker.py` | Mantém o MTTR acumulado em memória por execução do processo |
| `libs/sockets/status_usina.py` | Eventos Socket.IO de status, room por usina e intervenção manual |
| `libs/sockets/testar_leitura.py` | Evento Socket.IO para teste de uma leitura individual |
| `libs/sockets/ai_generation.py` | Evento Socket.IO para geração assistida de texto de RAT |

---

## Rotas HTTP e endpoints

### Autenticação

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET`, `POST` | `/login` | Login por usuário ou e-mail |
| `GET` | `/logout` | Encerra a sessão atual |

### Páginas HTML

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/` | Dashboard principal |
| `GET` | `/monitoramento` | Tela full screen de monitoramento |
| `GET` | `/usina/<sigla>` | Página individual da usina |
| `GET` | `/ocorrencias` | Tela de registro e resolução de ocorrências |
| `GET` | `/configuracoes` | Tela de configuração de usinas/dispositivos |
| `GET` | `/temperaturas` | Tela dedicada às temperaturas |
| `GET` | `/rats` | Listagem e indicadores de RAT |
| `GET` | `/criarrat` | Formulário de criação de RAT |
| `GET` | `/modificarrat` | Tela de edição sem RAT pré-selecionado |
| `GET` | `/modificarrat/<rat_id>` | Tela de edição de um RAT específico |

### APIs JSON e ações

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/salvar_ocorrencia` | Cria uma ocorrência |
| `GET` | `/listar_ocorrencias` | Lista ocorrências com filtros por query string |
| `PUT`, `POST` | `/resolver_ocorrencia/<id>` | Resolve uma ocorrência que requer ação |
| `GET` | `/configuracoes/carregar` | Retorna o JSON atual de usinas/dispositivos |
| `POST` | `/configuracoes/salvar` | Valida e salva o JSON de usinas/dispositivos |
| `POST` | `/rat/salvar` | Cria um RAT com serviços, materiais, fotos e assinaturas |
| `POST` | `/rat/upload_foto` | Faz upload isolado de foto para `assets/RAT/imgs` |
| `GET` | `/rat/ver/<rat_id>` | Retorna os dados completos de um RAT |
| `POST` | `/rat/atualizar` | Atualiza RAT, serviços, materiais e fotos |
| `POST` | `/rat/atualizar_status_financeiro` | Atualiza o status financeiro do RAT |
| `POST` | `/rat/deletar` | Exclui RAT, fotos e assinaturas |
| `GET` | `/rat/pdf/<rat_id>` | Gera PDF inline ou download (`?mode=download`) |
| `GET` | `/produtos/buscar` | Busca materiais/produtos por termo |
| `GET` | `/assets/<path:filename>` | Serve arquivos da pasta `assets/` |

### Rotas auxiliares

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/favicon.ico` | Ícone da aplicação |
| `GET` | `/.well-known/appspecific/com.chrome.devtools.json` | Resposta `204` para probe do Chrome DevTools |

---

## Eventos Socket.IO usados pela aplicação

| Direção | Evento | Uso |
| --- | --- | --- |
| Cliente → servidor | `solicitar_status_usinas` | Solicita payload completo das usinas |
| Servidor → cliente | `status_usinas_dados` | Retorna/propaga o status completo das usinas |
| Cliente → servidor | `entrar_usina_room` | Entra no room de uma usina |
| Cliente → servidor | `sair_usina_room` | Sai do room de uma usina |
| Cliente → servidor | `solicitar_status_usina` | Solicita payload reduzido de uma usina específica |
| Servidor → cliente | `status_usina_dados` | Retorna potência total e potência por dispositivo da usina |
| Cliente → servidor | `registrar_intervencao_status` | Registra override manual (`MANUTENCAO`, `RESTRICAO`, `NORMAL`) |
| Cliente → servidor | `testar_leitura` | Testa uma variável individual na tela de configuração |
| Servidor → cliente | `resultado_teste_leitura` | Resultado do teste de leitura |
| Cliente → servidor | `gerar_relatorio_ia` | Solicita texto assistido para RAT |
| Servidor → cliente | `relatorio_gerado_sucesso` | Retorna descrição/conclusão geradas |
| Servidor → cliente | `erro_ia` | Retorna falha de geração por IA |
| Servidor → cliente | `file_changed` | Disparado pelo watcher para recarregar páginas em desenvolvimento |

Além dos eventos sob demanda, a thread de coleta em `main.py` também emite `status_usinas_dados` em broadcast a cada ciclo.

---

## Estrutura real do arquivo `config/usinas_dispositivos.json`

O coletor e a tela de configuração trabalham com uma estrutura neste formato:

```json
{
  "Nome da Usina": {
    "ip": "10.0.0.10",
    "port": 8010,
    "table": "nome_tabela_opcional",
    "dispositivos": {
      "UG-01": {
        "conexao": {
          "ip": "192.168.0.10",
          "port": 502,
          "timeout": 3.0
        },
        "caracteristicas": {
          "potência máxima": 1350
        },
        "leituras": {
          "Potência Ativa": [13407, "REAL", {"offset": -1}],
          "US (sincronizado)": [20330, "BOOLEAN", {"offset": -1}],
          "Nivel montante": [13519, "REAL", {"offset": -1, "converter": "word_order"}]
        },
        "temperaturas": {
          "Mancal Guia value": [13463, "REAL", {"offset": -1}],
          "Mancal Guia alarmes": [13983, "REAL", {"offset": -1}],
          "Mancal Guia trip": [13919, "REAL", {"offset": -1}]
        },
        "alarmes": {},
        "comandos": {}
      }
    }
  }
}
```

### Como essa configuração é usada hoje

- A coleta contínua usa `conexao`, `leituras` e `temperaturas` para montar status, potência, níveis e temperaturas.
- Dispositivos com nome `PSA` são tratados como caso especial: não coletam status, potência e temperaturas, apenas leituras configuradas.
- A interface de configuração também permite persistir seções extras e testá-las individualmente via Socket.IO.
- Overrides manuais de status são gravados em `config/intervencoes_operador.json`.

---

## Fluxo de coleta em tempo real

1. `main.py` inicia Flask, Socket.IO, handlers e a thread `coletor_background_thread`.
2. A cada `INTERVALO_COLETA` segundos, a thread chama `coletar_status_completo()`.
3. `coletor_core.py` lê `config/usinas_dispositivos.json`, monta tarefas assíncronas por dispositivo e executa a coleta em paralelo.
4. `readRT.py` envia requisições HTTP para a API externa da usina (`/readCLP/leituras`) com os registradores que devem ser lidos.
5. O coletor consolida por usina:
   - status operacional por ordem de prioridade `US`, `UMD`, `UPS`, `UPGM`, `UP`;
   - potência ativa;
   - temperaturas;
   - níveis configurados.
6. Se existir intervenção manual (`MANUTENCAO` ou `RESTRICAO`) e a máquina não estiver gerando, o status exibido é sobrescrito.
7. O payload final:
   - atualiza o `mttr_tracker` em memória;
   - é salvo como JSON em `op_paradas`;
   - é emitido em `status_usinas_dados` para os clientes conectados.
8. Solicitações Socket.IO reutilizam um cache de 5 segundos para evitar coletas duplicadas fora do ciclo da thread.

### Temperaturas e risco

- A lista de temperaturas exibida na home e em `/temperaturas` é calculada a partir dos 10 snapshots mais recentes de `op_paradas`.
- Cada sensor é agrupado por nome, recebe histórico curto, valor atual, limiar de alarme, limiar de trip e um índice de risco calculado como `atual / trip`.
- A listagem é ordenada por risco decrescente.

### MTTR

- O MTTR mostrado na aplicação vem de `libs/servicos/mttr_tracker.py`.
- Esse cálculo é acumulado em memória a partir dos payloads em tempo real.
- Como consequência, o indicador reinicia quando o processo da aplicação reinicia.

---

## Uso de banco de dados

### Conexão

- O projeto usa `mysql-connector-python` com `MySQLConnectionPool`.
- O pool é singleton global e thread-safe.
- O tamanho do pool vem de `MYSQL_POOL_SIZE`.
- As operações de escrita usam `autocommit=False` com `commit` explícito em cada execução.
- Cada instância de `Database` devolve a conexão ao pool ao final da operação.

### Tabelas realmente usadas pelo código

| Tabela | Uso atual |
| --- | --- |
| `op_usina` | Cadastro das usinas exibidas em menus, home e páginas individuais |
| `op_usuario` | Operadores e técnicos usados em ocorrências e RATs |
| `op_ocorrencia` | Registro e resolução de ocorrências |
| `op_paradas` | Armazena snapshots JSON da coleta em tempo real |
| `clientes` | Cadastro de clientes/obras para RAT |
| `rats` | Cabeçalho e metadados do RAT |
| `rat_servicos` | Horas e executantes por RAT |
| `rat_materiais` | Materiais aplicados por RAT |
| `rat_fotos` | Fotos vinculadas ao RAT |
| `produtos` | Busca de materiais/produtos no módulo de RAT |

### Cache em memória

`DadosContexto` mantém cache local para reduzir leituras repetidas do banco:

| Chave | TTL / comportamento |
| --- | --- |
| `usinas` | 6 horas |
| `usuarios` | 6 horas |
| `ocorrencias_<limit>` | 6 horas com atualização incremental a cada 60 segundos |
| `stats_status` | 5 minutos |
| `kpis_mttr` | 5 minutos |
| `temperaturas` | 60 segundos |
| `ocorrencias_requer_acao` | 30 segundos |

---

## Autenticação e controle de acesso

- O login é feito por sessão Flask.
- Os usuários de acesso são definidos em memória em `libs/routes/routes.py`.
- O login aceita usuário ou e-mail.
- A opção "lembrar neste dispositivo" apenas marca a sessão como permanente.
- Existe rate limit em memória de 5 tentativas por IP a cada 5 minutos.
- Todas as rotas exigem autenticação, exceto:
  - `/login`
  - `/static/`
  - `/assets/`
  - `/socket.io/`
  - `/favicon.ico`
  - `/.well-known/appspecific/com.chrome.devtools.json`

Importante: `op_usuario` é usado para operadores/técnicos em formulários, mas não é a fonte de autenticação do sistema no estado atual.

---

## Fluxo de ocorrências

1. O operador acessa `/ocorrencias`.
2. Preenche dados básicos, tipo, categoria, data/hora, unidade, tags, playbook e descrição.
3. Se marcar `requer_acao`, a ocorrência é criada com status `aberta`.
4. Se não marcar `requer_acao`, a ocorrência é criada com status `cancelada`.
5. Ocorrências que requerem ação aparecem na aba de resolução e no cache `ocorrencias_requer_acao`.
6. A resolução exige `resolvida_por`, `data_resolucao` e `resolucao_descricao`.
7. Ao resolver, a ocorrência passa para `resolvida` e `requer_acao` volta para `0`.

---

## RAT e geração de PDF

### O que o módulo de RAT faz hoje

- Lista RATs com paginação, busca textual e KPIs do mês.
- Calcula horas totais por RAT e indicadores por prioridade, atividade, técnico e obra.
- Gera protocolo no formato `YYYYMMDD-XX`.
- Cria RAT com:
  - cabeçalho do atendimento;
  - serviços executados;
  - materiais aplicados;
  - fotos;
  - assinaturas em base64;
  - deslocamento;
  - status financeiro inicial.
- Permite editar descrição, conclusão, deslocamento, serviços, materiais, fotos e legendas.
- Permite atualizar o status financeiro de forma independente.
- Permite excluir RAT, fotos e assinaturas.
- Busca produtos por termo em `produtos`.

### Arquivos gerados pelo módulo

- Fotos enviadas por upload: `assets/RAT/imgs/`
- Fotos geradas a partir de base64 na edição: `assets/RAT/imgs/`
- Assinaturas: `assets/RAT/signatures/`

### PDF

- O endpoint `/rat/pdf/<rat_id>` renderiza o template `libs/views/components/_pdf_rats.html`.
- A geração é feita por `WeasyPrint`.
- O modo padrão é visualização inline; `?mode=download` força download.
- O PDF inclui logo, dados do cliente, dados do atendimento, serviços, materiais, fotos, assinaturas e total de horas calculado a partir dos intervalos de serviço.

### Geração assistida por IA

- O front envia `gerar_relatorio_ia` via Socket.IO.
- O backend usa `google.generativeai` com o modelo configurado em `libs/sockets/ai_generation.py`.
- A resposta esperada alimenta os campos de descrição das atividades e conclusão.
- Sem `GEMINI_API_KEY`, o backend retorna `erro_ia`.

---

## Dependências relevantes

| Dependência | Situação no projeto | Uso |
| --- | --- | --- |
| `Flask==3.0.0` | listada em `requeriments.txt` | aplicação web |
| `Flask-SocketIO==5.3.5` | listada | comunicação em tempo real |
| `mysql-connector-python==8.2.0` | listada | MySQL e pool de conexões |
| `python-dotenv==1.0.0` | listada | leitura do `.env` |
| `python-socketio==5.10.0` | listada | suporte ao ecossistema Socket.IO |
| `eventlet==0.33.3` | listada | instalada, mas não usada no `async_mode` atual |
| `watchdog==3.0.0` | listada | watcher de arquivos |
| `python-dateutil==2.8.2` | listada | utilidades de data |
| `httpx` | listada | cliente HTTP para a ponte de leitura dos CLPs |
| `werkzeug` | listada | uploads e utilitários HTTP |
| `WeasyPrint` | listada | geração de PDF |
| `google-generativeai` | usada no código, não listada em `requeriments.txt` | geração assistida por IA para RAT |

---

## Referências internas úteis

- `config/usinas_dispositivos.json`: configuração das usinas e dispositivos lida pelo coletor.
- `config/README.md`: documentação complementar do JSON de configuração.
- `libs/models/docs/`: scripts auxiliares de seed, migração e testes locais de banco.
- `testes/`: testes e scripts de apoio para a camada de modelos.
