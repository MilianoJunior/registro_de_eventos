# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _periodo_para_intervalo -> define a janela de consulta por período
# 2. Read -> repositório genérico para leituras SQL
# 3. OpParadas.get_mttr_diario_all -> retorna eventos para cálculo de MTTR
# -------------------------------------------------------------------

# libs/models/read.py
from __future__ import annotations

# CONFIGURAÇÕES / CONSTANTES / MAPAS
PERIODOS_PARADAS = {'diario': 1, 'semanal': 7, 'mensal': 30, 'anual': 365}
from datetime import datetime, timedelta
from typing import Optional, Sequence, Union, Any, Dict, List, Tuple
import json
from libs.models.database import Database
from libs.models.utils.utils import (
    safe_ident, columns_sql, build_where_clause,
    order_sql, limit_sql,
)


def _periodo_para_intervalo(periodo: str) -> datetime:
    dias = PERIODOS_PARADAS.get(periodo, PERIODOS_PARADAS['diario'])
    return datetime.now() - timedelta(days=dias)

Identifier = str
Columns = Union[str, Sequence[Identifier]]

class Read:
    """
    Repositório de leitura simples (parametrizado, reutilizável).
    """
    def __init__(
        self,
        tabela: Identifier,
        colunas: Optional[Columns] = None,
        default_order_by: Optional[Identifier] = "id",
        default_desc: bool = False,
        db_instance: Optional[Database] = None,
    ):
        self.tabela = tabela
        self.colunas = colunas if colunas is not None else "*"
        self.default_order_by = default_order_by
        self.default_desc = default_desc
        self.db = db_instance or Database()

    # ----------------- leituras básicas -----------------
    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Identifier] = None,
        desc: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        try:
            import time
            self.db.connect()
            cols = columns_sql(self.colunas)
            sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"
            sql += order_sql(order_by or self.default_order_by, self.default_desc if desc is None else bool(desc))
            sql += limit_sql(limit, offset)
            dados = self.db.fetch_data(sql)
            return dados
        except Exception as e:
            self._error('Read', 'get_all', e)

    def get_by_id(self, id_: int) -> Optional[Dict[str, Any]]:
        try:
            self.db.connect()
            cols = columns_sql(self.colunas)
            sql = f"SELECT {cols} FROM {safe_ident(self.tabela)} WHERE `id` = %s LIMIT 1"
            rows = self.db.fetch_data(sql, (id_,))
            return rows[0] if rows else None
        except Exception as e:
            self._error('Read', 'get_by_id', e)

    def first(
        self,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[Identifier] = None,
        desc: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        rows = self.where(where or {}, limit=1, order_by=order_by, desc=desc)
        return rows[0] if rows else None

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        try:
            self.db.connect()
            sql = f"SELECT COUNT(*) AS total FROM {safe_ident(self.tabela)}"
            params: List[Any] = []
            if where:
                clause_params = build_where_clause(where)
                clause, params = clause_params if clause_params else ("", [])
                sql += clause
            rows = self.db.fetch_data(sql, tuple(params))
            return int(rows[0]["total"]) if rows else 0
        except Exception as e:
            self._error('Read', 'count', e)

    # ----------------- filtros/where -----------------
    def where(
        self,
        where: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Identifier] = None,
        desc: Optional[bool] = None,
        columns: Optional[Columns] = None,
    ) -> List[Dict[str, Any]]:
        """
        Operadores suportados (ver utils.build_where_clause):
          =, IN, LIKE, LIKE_NORM, EQ_NORM, STARTSWITH_NORM, ENDSWITH_NORM,
          NE, GT, GTE, LT, LTE, REGEXP
        """
        try:
            self.db.connect()
            cols = columns_sql(columns if columns is not None else self.colunas)
            sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"
            clause_params = build_where_clause(where)
            clause, params = clause_params if clause_params else ("", [])
            sql += clause
            sql += order_sql(order_by or self.default_order_by, self.default_desc if desc is None else bool(desc))
            sql += limit_sql(limit, offset)
            return self.db.fetch_data(sql, tuple(params))
        except Exception as e:
            self._error('Read', 'where', e)

    # ----------------- intervalos de data -----------------
    def get_between(
        self,
        column: Identifier = "created_at",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Identifier] = None,
        desc: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        try:
            self.db.connect()
            col = safe_ident(column)
            cols = columns_sql(self.colunas)

            conds: List[str] = []
            params: List[Any] = []

            if start is not None:
                conds.append(f"{col} >= %s")
                params.append(start)
            if end is not None:
                conds.append(f"{col} <= %s")
                params.append(end)

            sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"
            if conds:
                sql += " WHERE " + " AND ".join(conds)

            sql += order_sql(order_by or self.default_order_by, self.default_desc if desc is None else bool(desc))
            sql += limit_sql(limit, offset)
            return self.db.fetch_data(sql, tuple(params))
        except Exception as e:
            self._error('Read', 'get_between', e)

    # ----------------- utilidades -----------------
    def ids_only(self, where: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[int]:
        try:
            self.db.connect()
            sql = f"SELECT `id` FROM {safe_ident(self.tabela)}"
            params: List[Any] = []
            if where:
                clause_params = build_where_clause(where)
                clause, params = clause_params if clause_params else ("", [])
                sql += clause
            sql += limit_sql(limit, 0)
            rows = self.db.fetch_data(sql, tuple(params))
            return [int(r["id"]) for r in rows]
        except Exception as e:
            self._error('Read', 'ids_only', e)

    def _error(self, name, function, e):
        raise Exception(f"Erro: class: {name}, function: {function}: msg: {e}")

# ----------------- Models "fininhos" (op_) -----------------
class OpUsina(Read):
    def __init__(self, colunas: Optional[Columns] = None, db_instance: Optional[Database] = None):
        super().__init__(
            "op_usina",
            colunas or ["id", "nome", "sigla", "ativo", "created_at"],
            default_order_by="nome",
            db_instance=db_instance,
        )

class OpUsuario(Read):
    def __init__(self, colunas: Optional[Columns] = None, db_instance: Optional[Database] = None):
        super().__init__(
            "op_usuario",
            colunas or ["id", "nome", "email", "perfil", "ativo"],
            default_order_by="nome",
            db_instance=db_instance,
        )

class OpOcorrencia(Read):
    def __init__(self, colunas: Optional[Columns] = None, db_instance: Optional[Database] = None):
        super().__init__(
            "op_ocorrencia",
            colunas or [
                "id","usina_id","operador_id","tipo","categoria","unidade","tags",
                "playbook","template_texto","descricao",
                "status","severidade","origem","metadata",
                "created_at","updated_at","resolved_at",
                "requer_acao","data_ocorrencia","resolvida_por","resolucao_descricao"
            ],
            default_order_by="created_at",
            default_desc=True,
            db_instance=db_instance,
        )

    def get_counts_by_status(self) -> Dict[str, int]:
        """Retorna contagem agrupada por status"""
        sql = "SELECT status, COUNT(*) as total FROM op_ocorrencia GROUP BY status"
        res = self.db.fetch_data(sql)
        if not res:
            return {}
        return {r['status']: r['total'] for r in res}

    def get_open_actions(self, limit=20) -> List[Dict]:
        """Busca ocorrências que requerem ação e não estão resolvidas por completo"""
        # Regra: requer_acao=1 E (resolvida_por IS NULL OR resolvida_por = '')
        # Ajuste conforme a regra exata do usuário
        return self.get_all(
            conditions={
                "requer_acao": 1,
                # Opcional: adicionar filtro de resolvida_por se o método get_all suportar IS NULL ou custom query
            },
            limit=limit
        )


class OpParadas(Read):
    def __init__(self, colunas: Optional[Columns] = None, db_instance: Optional[Database] = None):
        super().__init__(
            "op_paradas",
            colunas or ["id", "timestamp", "dados"],
            default_order_by="timestamp",
            default_desc=True,
            db_instance=db_instance,
        )
    def get_indicadores_manutencao(self, periodo: str = 'diario') -> Dict[str, Any]:
        """
        Calcula MTTR e tempo de indisponibilidade baseado no histórico de snapshots.
        Retorna: { 'slug_usina': { 'mttr_str': '2h 15m', 'mttr_minutos': 135, ... } }
        """
        try:
            janela = _periodo_para_intervalo(periodo)
            self.db.connect()
            # Ordenado ASC para calcular a linha do tempo corretamente
            sql = f"SELECT timestamp, dados FROM {safe_ident(self.tabela)} WHERE `timestamp` >= %s ORDER BY `timestamp` ASC"
            rows = self.db.fetch_data(sql, (janela,))
            
            if not rows:
                return {}

            # Estruturas acumuladoras
            # stats[slug_usina][nome_dispositivo] = { 'tempo_manutencao': 0, 'contagem': 0, 'em_manutencao': False }
            stats = {}

            for i in range(len(rows) - 1):
                atual = rows[i]
                proximo = rows[i+1]
                
                # Delta T em minutos
                dt_seconds = (proximo['timestamp'] - atual['timestamp']).total_seconds()
                dt_minutes = dt_seconds / 60.0
                
                # Evitar deltas gigantes (se o coletor ficou desligado 1 dia, não conta como manutenção)
                if dt_minutes > 60: 
                    continue

                dados = atual['dados']
                if isinstance(dados, str):
                    try:
                        dados = json.loads(dados)
                    except:
                        continue
                
                # Estrutura do JSON: { 'usinas': [ { 'slug': '...', 'dispositivos': { ... } } ] }
                lista_usinas = dados.get('usinas', [])
                
                for usina in lista_usinas:
                    slug = usina.get('slug')
                    if not slug: continue
                    
                    if slug not in stats: stats[slug] = {}
                    
                    dispositivos = usina.get('dispositivos', {})
                    for nome_disp, info in dispositivos.items():
                        if nome_disp not in stats[slug]:
                            stats[slug][nome_disp] = {'tempo_manutencao': 0.0, 'eventos': 0, 'ultimo_status_era_manutencao': False}
                        
                        # Verifica status
                        descricao = (info.get('descricao') or "").lower()
                        em_manutencao = "manutenção" in descricao
                        
                        # Contabiliza tempo
                        if em_manutencao:
                            stats[slug][nome_disp]['tempo_manutencao'] += dt_minutes
                            
                        # Contabiliza eventos (borda de subida)
                        if em_manutencao and not stats[slug][nome_disp]['ultimo_status_era_manutencao']:
                            stats[slug][nome_disp]['eventos'] += 1
                            
                        stats[slug][nome_disp]['ultimo_status_era_manutencao'] = em_manutencao

            # Consolidar resultados por Usina
            resultados = {}
            for slug, disps in stats.items():
                tempo_total_usina = 0.0
                eventos_total_usina = 0
                
                for d in disps.values():
                    tempo_total_usina += d['tempo_manutencao']
                    eventos_total_usina += d['eventos']
                
                # MTTR da Usina (Média simples ou soma? Normalmente soma do tempo / soma dos eventos)
                mttr_minutos = 0
                if eventos_total_usina > 0:
                    mttr_minutos = tempo_total_usina / eventos_total_usina
                elif tempo_total_usina > 0:
                    # Se tem tempo mas não pegou o inicio do evento (evento veio de antes), considera 1 evento
                    mttr_minutos = tempo_total_usina
                
                # Formatação amigável
                horas = int(mttr_minutos // 60)
                minutos = int(mttr_minutos % 60)
                mttr_str = f"{horas}h {minutos}m" if horas > 0 else f"{minutos} min"
                
                resultados[slug] = {
                    'mttr_str': mttr_str if mttr_minutos > 0 else "0 min",
                    'mttr_minutos': mttr_minutos,
                    'eventos': eventos_total_usina
                }
                
            return resultados

        except Exception as e:
            self._error('Read', 'get_indicadores_manutencao', e)
            return {}

'''
Labels de status:
    "UP (parada)",
    "UPGM (pronta para giro mecânico)",
    "UMD (marcha desexcitada)",
    "UPS (pronta para sincronização)",
    "US (sincronizado)",
    "Manutenção (parada)",
    "Restrição da concessionária (parada)",
    "Sem conexão",


A lógica segue a sequência de partida da máquina, lendo os "leds" virtuais presentes nos blocos centrais da imagem (U.P., U.P.G.M., U.M.D., U.P.S. e U.S.):

Aqui está a descrição completa:

1. U.P. (Parada) - Unidade Parada

   - A turbina está parada.
   - Unidade Hidráulica de Lubrificação dos Mancais (U.H.L.M.) está desligada.
   - Unidade Hidráulica de Regulação de Velocidade (U.H.R.V.) está desligada.
   - ByPass (de água) está fechado.
   - Válvula Borboleta da turbina está fechada.

2. U.P.G.M. (Pronta para Giro Mecânico) - Unidade Pronta para Giro Mecânico

   - U.H.L.M. está operacional (sistema de lubrificação ativo).
   - U.H.R.V. está operacional (sistema de regulação de velocidade ativo).
   - S.F.A. (Sistema de Filtragem de Água) está operacional.
   - Válvula Borboleta está aberta (permitindo a passagem de água até o distribuidor).
   - Turbina em estado operacional (condições de segurança satisfeitas para início do giro).

3. U.M.D. (Marcha Desexcitada) - Unidade em Marcha Desexcitada

   - R.V. (Regulador de Velocidade) Habilitado: O controle de velocidade da turbina está ativo.
   - Válv. Seg. Distribuidor: A Válvula de Segurança do Distribuidor está atuada/aberta.
   - Velocidade 90%: A turbina atingiu 90% da sua rotação nominal (mas ainda não há tensão nos terminais do gerador pois a excitação está desligada).

4. U.P.S. (Pronta para Sincronização) - Unidade Pronta para Sincronização

   - R.T. (Regulador de Tensão) Habilitado: O sistema de excitação foi ligado.
   - Tensão 90%: A tensão nos terminais do gerador atingiu 90% do valor nominal (a máquina já está gerando tensão, aguardando apenas o ajuste fino para sincronismo).
   - 5. U.S. (Sincronizado) - Unidade Sincronizada
   - Sincr. Habilitado: O relé ou sistema de sincronismo permitiu a operação.
   - Disj. 52G Fechado: O Disjuntor do Gerador (código ANSI 52) está fechado, conectando a usina à rede elétrica ou ao barramento de carga. A unidade está efetivamente gerando energia.

5. U.S. (Sincronizado) - Unidade Sincronizada

   - Sincr. Habilitado: O relé ou sistema de sincronismo permitiu a operação.
   - Disj. 52G Fechado: O Disjuntor do Gerador (código ANSI 52) está fechado, conectando a usina à rede elétrica ou ao barramento de carga. A unidade está efetivamente gerando energia.

6. Sem conexão

    Indica falha de comunicação entre o sistema de supervisão (a tela que estamos vendo) e o CLP (Controlador Lógico Programável) da usina. Neste estado, os valores mostrados na tela (geralmente representados por ####) não são confiáveis ou não estão sendo atualizados.

7. Manutenção

    Indica que a usina está em manutenção corretiva ou preventiva, parada para realizar troca de peças, reparos, etc.

8. Restrição da concessionária

    Indica que a usina está em restrição da concessionária, ou seja, está parada ou sem conexão devidos a eventos externos, geralmente interrompe a energia na linha e provoca o acionamento do gerador e proteções.

Para efeitos de procedimentos de rede do ONS, as categorias de parada a TEIF - Taxa de Indisponibilidade Forçada - são:

    1.Indisponibilidade Programada (IP): Manutenção preventiva agendada. (A usina não é penalizada se cumprir o prazo).
    2.Indisponibilidade Forçada (IF): Quebra, defeito ou trip. (A usina é penalizada).
    3.Indisponibilidade Externa: Linha de transmissão caiu, ONS mandou cortar geração. (Isenta de responsabilidade).
    4.Indisponibilidade Hidráulica: Falta de água ou cheia excessiva. (Isenta, mas precisa provar cota/nível).

Minha classificação inicial é uma cobertura generalista que vai justificar a classificação da ONS, no entanto, minha duvida e se a interface do softwaredeve cobrir esses procedimentos ou ele deve ser apresentado como informação de relatorio gerado pelo software.

Em todas as etapas de transição de status, exceto "Status sincronizado", devem ser calculados como usina parada, no entanto,
tenho que diferenciar esse verificação, por que as transições de status para efeito de analise de eficiência são etapas necessárias e de caracteristica de projeto.
Sendo assim, na interface de operação, tenho o MTTR (Tempo Médio de Parada), mas estou pensando em acrescentar um valor percentual para cada estado, e o MTTR ser um total não qualitativo.
Dai então, criar um outro indicador qualitativo, que desconsidera etapas necessarias de transição, desconsidera quando o nivel de água montante estiver abaixo do nivel de segurança ou quando a usina está desligada para aumentar o nível montante em níveis de retorno a operação. 

'''
'''
Aqui está minha análise técnica como Engenheiro de Software Sênior focado no domínio de hidrelétricas, baseada nos dados de log, na estrutura do `read.py` e na interface apresentada.

### 1. O Problema Conceitual do MTTR Atual
Na sua interface e lógica atual, qualquer estado diferente de "US (sincronizado)" parece estar penalizando o indicador de parada (MTTR). Isso é um erro conceitual grave para sistemas de energia.

*   **Transições (UPGM, UMD, UPS):** São etapas **operacionais**, não falhas. Uma máquina levar 5 minutos para sincronizar faz parte do *Tempo de Partida*, não do *Tempo de Reparo*.
*   **Restrição Hídrica (Nível Baixo):** Se a máquina para porque não tem água, a usina está **Disponível**, mas indisposta por recurso. Isso não deve contar como falha mecânica/elétrica.

### 2. Proposta de Novos Indicadores (Qualitativos)
Para resolver a questão levantada no `read.py` (linhas 306-309), sugiro separar o "tempo não produtivo" em três categorias distintas ("buckets") para o cálculo nos períodos (diário, semanal, etc):

#### A. Disponibilidade Física (Availability)
A métrica mais honesta para a manutenção.
*   **Fórmula:** `(Tempo Total - Tempo em Falha/Manutenção) / Tempo Total`
*   **Lógica:** Só penaliza se o status for "Sem conexão", "Erro" ou se houver um *flag* explícito de manutenção.
*   **Impacto:** Se a máquina está `UP (parada)` aguardando chuva, a disponibilidade é 100%.

#### B. Fator de Capacidade (Capacity Factor)
Métrica financeira/geração.
*   **Fórmula:** `Geração Real (MW médio) / Capacidade Instalada (MW)`
*   **Lógica:** Usa diretamente o sensor de "Potência Ativa".
*   **Impacto:** Mostra o quanto a usina está entregando do que ela foi projetada para entregar.

#### C. Eficiência de Partida (Startup Performance)
Métrica específica para as transições (UPGM → UMD → UPS → US).
*   **Conceito:** Monitorar a duração média que a UG fica nesses estados intermediários.
*   **Alerta:** Se o tempo médio de `UPS (pronta para sincronização)` começar a subir, indica problema no regulador de tensão ou no relé de sincronismo, antes mesmo de gerar uma falha.

### 3. Estratégia de Dados (Considerando o JSON atual)
Olhando seus logs (`3525-3643`), temos timestamps precisos e status por UG. Como uma usina tem N UGs (ex: PCH PEDRAS tem UG-01 e UG-02):

1.  **Cálculo Granular (Por UG):** Os indicadores devem ser calculados individualmente por UG. O indicador da Usina é a média ponderada (pela potência nominal) das UGs.
2.  **Detecção de "Parada Hídrica":**
    *   *Desafio:* O JSON atual não traz o "Nível Montante".
    *   *Solução Imediata:* Se `Status == UP` E `Erro == null`, classifique como **"Reserva Operacional"** (não penaliza MTTR).
    *   *Solução Ideal:* Adicionar leitura do nível no JSON e cruzar: `Se (Status == UP) AND (Nivel < Setpoint)`, então `Motivo = Hídrico`.

### 4. Resumo da Sugestão para a Interface
Substitua ou complemente o card único de "MTTR" por uma barra de composição (Stacked Bar) ou três KPIs menores:

1.  **Disponibilidade:** XX.X% (Tempo que a máquina *poderia* rodar).
2.  **Geração:** XX.X% (Tempo em `US`).
3.  **Reserva:** XX.X% (Tempo em `UP` sem erro + Transições).

**Conclusão:**
Mantenha o MTTR **apenas** para falhas reais (trips/erros). Crie um indicador separado chamado "Tempo em Reserva" para os momentos em que a usina está parada por decisão operacional ou falta de água. As transições devem ser somadas ao tempo de operação ou reserva, nunca ao tempo de reserva, nunca ao tempo de reserva, nunca ao tempo de prontidão, jamais como falha.

'''
'''
"Erro" ou se houver um flag explícito de manutenção.
    

'''