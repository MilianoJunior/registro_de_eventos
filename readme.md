
## Propósito
Reduzir paradas e custo operacional em CGHs/PCHs transformando sinais e registros em ações padronizadas, notificações úteis e relatórios automáticos para o cliente.
Nosso software existe para transformar eventos em decisões e resultados: menos paradas, mais energia faturada e relatórios automáticos — com uma rotina tão simples que o operador quer usar.

## Requisitos

Com poucos cliks:
- O operador deve registrar um novo evento;
- O gerenciador deve saber os principais eventos em todas as usinas monitoradas;
- O sistema deve priorizar os eventos que podem ser mais críticos, então os eventos devem seguir uma classificação;

Pagina - Home

Descrição: Página principal que deve mostrar uma visão geral e conter no máxima 6 usinas, 
dividido em 2 linhas e 3 colunas de forma responsiva. 
Será feito um roteamento dessa pagina home para mostrar mais usinas em outras paginas pelo naveador.

KPI - Key Performance Indicador(Indicador chave de desempenho)

Para cada op_usina e cada Unidade Geradora(UG):

Indicador se a UG está parada ou operacional e botão que leva a tela personalizada da op_usina com mais informações;
Quanto cada UG gerou de potência - geração instantânea, dia, mês; 
Nível montante(Valor comum entre as UG's) e jusante(Valor individual para cada UG)  - instantânea, taxa de variação(mma(12 min)), dia, mês e diferêncial de grade (nível montante - nível jusante);
Temperaturas de todas as usinas, ordenadas pelo valor do maior risco, com valores de alarme e trip, onde o risco é calculado pela razão entre o valor atual e o TRIP;
Display de eventos para cada UG e botão para inserir manualmente um novo evento, devem ser definidos cores para a prioridades dos eventos;

Os Eventos devem conter as seguintes colunas: 

id BIGINT PRIMARY KEY AUTO_INCREMENT,
usina_id BIGINT NOT NULL,
ug_id BIGINT NULL,
operador_id BIGINT NULL,                         -- quem registrou/ack
origem ENUM('SCADA','CLP','API','MANUAL','SENSOR','TRANSFORMADOR','CELESC') NOT NULL,
tipo   ENUM('evento','alarme','comando') NOT NULL,
categoria_id INT NOT NULL,
prioridade ENUM('baixa','media','alta') NOT NULL,
titulo VARCHAR(160) NOT NULL,
descricao TEXT,
tag VARCHAR(120),
valor DECIMAL(18,6) NULL,
unidade_medida VARCHAR(16),
ts_inicio DATETIME(6) NOT NULL,
ts_fim DATETIME(6) NULL,
estado ENUM('novo','ativo','reconhecido','investigando','resolvido','cancelado')NOT NULL DEFAULT 'novo',

Pagina - novo

Descrição: Registro do novo evento.

Pagina - usinas

Descrição: Pagina personalizada para cada op_usina, com graficos e informações mais detalhadas

Pagina - Configurações

Pagina - para configurar as variaveis que alteram o desempenho do COG.

Nesse primeiro momento, vamos fazer apenas a pagina Home, e partir do projeto em anexo, os dados de leitura do tempo real já estão sendo realizadas corretamente, vamos considerar que isso vai ser um MVP,
e que depois vamos melhorar, não vamos inserir muita complexibilidade e alterar a lógica de leitura, o registro de eventos vamos fazer depois, deixe e


