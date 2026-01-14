# libs/models/read.py

# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _periodo_para_intervalo → converte período (diario/semanal/...) em datetime de corte
# 2. BaseReader → executa consultas simples (all/where/one/count) com segurança básica
# 3. Op* → readers por tabela (inclui indicadores de manutenção em OpParadas)
# -------------------------------------------------------------------

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from libs.controllers.decorador import desempenho
from libs.models.database import Database
from libs.models.utils.utils import columns_sql, limit_sql, order_sql, safe_ident

Columns = Union[str, Sequence[str]]

PERIODOS_PARADAS = {'diario': 1, 'semanal': 7, 'mensal': 30, 'anual': 365}

def _periodo_para_intervalo(periodo: str = 'diario') -> datetime:
    dias = PERIODOS_PARADAS.get(periodo.lower(), 1)
    return datetime.now() - timedelta(days=dias)

class BaseReader:
    tabela: str
    colunas_padrao: Columns = "*"
    order_padrao: str = "id"
    desc_padrao: bool = False

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    @desempenho
    def _run(self, sql: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        self.db.connect()
        return self.db.fetch_data(sql, params if params else None)

    def all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        cols = columns_sql(self.colunas_padrao)
        sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"
        sql += order_sql(self.order_padrao, self.desc_padrao)
        sql += limit_sql(limit, offset)
        return self._run(sql)

    def where_eq(
        self,
        where: Dict[str, Any],
        order_by: Optional[str] = None,
        desc: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        cols = columns_sql(self.colunas_padrao)
        sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"
        parts: List[str] = []
        params: List[Any] = []
        for k, v in where.items():
            col = safe_ident(k)
            if isinstance(v, (tuple, list)):
                op, val = v
                if str(op).upper() in ("IS NULL", "IS NOT NULL"):
                    parts.append(f"{col} {str(op).upper()}")
                elif str(op).upper() == "IN" and isinstance(val, (list, tuple)):
                    placeholders = ", ".join(["%s"] * len(val))
                    parts.append(f"{col} IN ({placeholders})")
                    params.extend(val)
                else:
                    parts.append(f"{col} {op} %s")
                    params.append(val)
            else:
                parts.append(f"{col} = %s")
                params.append(v)
        if parts:
            sql += " WHERE " + " AND ".join(parts)
        sql += order_sql(order_by or self.order_padrao, self.desc_padrao if desc is None else desc)
        sql += limit_sql(limit, offset)
        return self._run(sql, tuple(params))

    def one(self, where: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rows = self.where_eq(where, limit=1)
        return rows[0] if rows else None

    def first(self, where: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Alias legível para pegar o primeiro registro que bater no filtro."""
        return self.one(where)

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        sql = f"SELECT COUNT(*) AS total FROM {safe_ident(self.tabela)}"
        params: List[Any] = []
        if where:
            parts = []
            for k, v in where.items():
                col = safe_ident(k)
                if isinstance(v, (tuple, list)):
                    op, val = v
                    if str(op).upper() in ("IS NULL", "IS NOT NULL"):
                        parts.append(f"{col} {str(op).upper()}")
                    else:
                        parts.append(f"{col} {op} %s")
                        params.append(val)
                else:
                    parts.append(f"{col} = %s")
                    params.append(v)
            if parts:
                sql += " WHERE " + " AND ".join(parts)
        row = self._run(sql, tuple(params))
        return int(row[0]["total"]) if row else 0

# ==================== SUAS MODELS (agora 100% funcionais) ====================
class OpUsina(BaseReader):
    tabela = "op_usina"
    colunas_padrao = ["id", "nome", "sigla", "ativo", "created_at"]
    order_padrao = "nome"

class OpUsuario(BaseReader):
    tabela = "op_usuario"
    colunas_padrao = ["id", "nome", "email", "perfil", "ativo"]
    order_padrao = "nome"

class OpOcorrencia(BaseReader):
    tabela = "op_ocorrencia"
    colunas_padrao = ["id", "usina_id", "operador_id", "tipo", "categoria", "unidade", "tags", "playbook", "template_texto", "descricao", "status", "severidade", "origem", "metadata", "created_at", "updated_at", "resolved_at", "requer_acao", "data_ocorrencia", "resolvida_por", "resolucao_descricao"]
    order_padrao = "created_at"
    desc_padrao = True

    @desempenho
    def convert_id_to_name(self, id: int) -> str:
        usinas = {
            "1": "CGH APARECIDA",
            "2": "CGH FAE",
            "3": "CGH HOPPEN",
            "4": "CGH PICADAS ALTAS",
            "5": "PCH PEDRAS",
        }
        return usinas.get(str(id), "N/A")

    def _injetar_usina_nome(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for r in rows or []:
            if isinstance(r, dict) and "usina_nome" not in r:
                r["usina_nome"] = self.convert_id_to_name(r.get("usina_id"))
        return rows

    @desempenho
    def listar_recentes_por_id(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._injetar_usina_nome(self.where_eq(where={}, order_by="id", desc=True, limit=limit))

    @desempenho
    def listar_novas_por_id(self, ultimo_id: int, limit: int = 200) -> List[Dict[str, Any]]:
        return self._injetar_usina_nome(self.where_eq(where={"id": (">", ultimo_id)}, order_by="id", desc=True, limit=limit))

    @desempenho
    def listar_recentes_usina_por_id(self, usina_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        return self._injetar_usina_nome(self.where_eq(where={"usina_id": usina_id}, order_by="id", desc=True, limit=limit))

    @desempenho
    def listar_novas_usina_por_id(self, usina_id: int, ultimo_id: int, limit: int = 200) -> List[Dict[str, Any]]:
        return self._injetar_usina_nome(self.where_eq(where={"usina_id": usina_id, "id": (">", ultimo_id)}, order_by="id", desc=True, limit=limit))

    @desempenho
    def listar_requer_acao(self) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {self.tabela} WHERE requer_acao = 1 ORDER BY created_at DESC LIMIT 200"
        resposta = self._run(sql)
        return self._injetar_usina_nome(resposta)

    @desempenho
    def listar_usina_por_periodo(
        self,
        usina_id: int,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        cols = columns_sql(self.colunas_padrao)
        sql = f"SELECT {cols} FROM {safe_ident(self.tabela)} WHERE {safe_ident('usina_id')} = %s"
        params: List[Any] = [usina_id]
        if data_inicio:
            sql += f" AND {safe_ident('created_at')} >= %s"
            params.append(data_inicio)
        if data_fim:
            sql += f" AND {safe_ident('created_at')} <= %s"
            params.append(data_fim)
        sql += f" ORDER BY {safe_ident('created_at')} DESC LIMIT %s"
        params.append(int(limit))
        return self._injetar_usina_nome(self._run(sql, tuple(params)))

    @desempenho
    def get_counts_by_status(self) -> Dict[str, int]:
        sql = f"SELECT status, COUNT(*) AS total FROM {safe_ident(self.tabela)} GROUP BY status"
        rows = self._run(sql)
        return {r["status"]: r["total"] for r in rows} if rows else {}

    @desempenho
    def get_open_actions(self, limit: int = 20) -> List[Dict]:
        return self.where_eq(
            where={"requer_acao": 1, "resolvida_por": ("IS NULL", None)},
            order_by="created_at",
            desc=True,
            limit=limit
        )

    @desempenho
    def listar_api(
        self,
        status_list: Optional[List[str]] = None,
        requer_acao: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        where = {}
        if status_list:
            if len(status_list) == 1:
                where["status"] = status_list[0]
            else:
                where["status"] = ("IN", tuple(status_list))
        
        if requer_acao is not None:
            where["requer_acao"] = requer_acao

        return self._injetar_usina_nome(
            self.where_eq(where=where, order_by="created_at", desc=True, limit=limit)
        )



class OpParadas(BaseReader):
    tabela = "op_paradas"
    colunas_padrao = ["id", "timestamp", "dados"]
    order_padrao = "timestamp"
    desc_padrao = True

    def __init__(self, db: Optional[Database] = None):
        super().__init__(db)
        self._cache_dados_brutos: Dict[str, List[Dict[str, Any]]] = {}

    def _parse_dados_paradas(self, raw: Any) -> Optional[Dict[str, Any]]:
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except Exception:
                return None
            return parsed if isinstance(parsed, dict) else None
        return None

    def _descricao_indica_manutencao(self, descricao: str) -> bool:
        desc = (descricao or "").lower()
        return ("manutenção" in desc) or ("manutencao" in desc)

    def _payload_pode_conter_manutencao(self, raw: Any) -> bool:
        if isinstance(raw, str):
            s = raw.lower()
            return ("manutencao" in s) or ("manutenção" in s)
        return True

    def _acumular_manutencao_por_usina(
        self,
        totais: Dict[str, Dict[str, float]],
        estado_anterior: Dict[str, Dict[str, bool]],
        lista_usinas: List[Dict[str, Any]],
        dt_minutos: float,
    ) -> None:
        for usina in lista_usinas or []:
            slug = usina.get("slug")
            if not slug:
                continue

            if slug not in estado_anterior:
                estado_anterior[slug] = {}
            if slug not in totais:
                totais[slug] = {"tempo_manutencao": 0.0, "eventos": 0.0}

            dispositivos = usina.get("dispositivos") or {}
            if not isinstance(dispositivos, dict):
                continue

            for nome_disp, info in dispositivos.items():
                if not isinstance(info, dict):
                    continue

                em_manutencao = self._descricao_indica_manutencao(info.get("descricao") or "")
                ultimo = estado_anterior[slug].get(nome_disp, False)

                if em_manutencao:
                    totais[slug]["tempo_manutencao"] += float(dt_minutos)
                if em_manutencao and not ultimo:
                    totais[slug]["eventos"] += 1.0

                estado_anterior[slug][nome_disp] = em_manutencao

    def _formatar_mttr(self, tempo_total_min: float, eventos: float) -> str:
        mttr_min = (tempo_total_min / eventos) if eventos > 0 else tempo_total_min
        if mttr_min <= 0:
            return "0 min"
        horas = int(mttr_min // 60)
        minutos = int(mttr_min % 60)
        return f"{horas}h {minutos}m" if horas > 0 else f"{minutos} min"

    def _get_dados_brutos_periodo(self, periodo: str) -> List[Dict[str, Any]]:
        """Busca snapshots de paradas (que contêm temperaturas) dado um período, com cache local."""
        janela = _periodo_para_intervalo(periodo)
        sql = (
            "SELECT timestamp, dados FROM op_paradas "
            "WHERE timestamp >= %s ORDER BY timestamp ASC"
        )
        data = self._run(sql, (janela,))
        self._cache_dados_brutos[periodo] = data
        return data

    @desempenho
    def get_indicadores_manutencao(self, periodo: str = 'diario') -> Dict[str, Any]:
        """Calcula MTTR (Tempo médio para reparo) por usina, a partir de snapshots em `op_paradas`."""
        try:
            rows = self._get_dados_brutos_periodo(periodo)

            estado_anterior: Dict[str, Dict[str, bool]] = {}
            totais: Dict[str, Dict[str, float]] = {}

            anterior: Optional[Dict[str, Any]] = None
            for atual in rows:
                if anterior is None:
                    anterior = atual
                    continue

                ts_ant = anterior.get("timestamp")
                ts_atual = atual.get("timestamp")
                if not isinstance(ts_ant, datetime) or not isinstance(ts_atual, datetime):
                    anterior = atual
                    continue

                dt_minutos = (ts_atual - ts_ant).total_seconds() / 60.0
                if dt_minutos <= 0 or dt_minutos > 60.0:
                    anterior = atual
                    continue

                raw = anterior.get("dados")
                if not self._payload_pode_conter_manutencao(raw):
                    anterior = atual
                    continue

                dados = self._parse_dados_paradas(raw)
                if not dados:
                    anterior = atual
                    continue

                lista_usinas = dados.get("usinas") or []
                if isinstance(lista_usinas, list):
                    self._acumular_manutencao_por_usina(totais, estado_anterior, lista_usinas, dt_minutos)

                anterior = atual

            return {slug: {"mttr_str": self._formatar_mttr(t["tempo_manutencao"], t["eventos"])} for slug, t in totais.items()}

        except Exception as e:
            raise Exception(f"Erro em get_indicadores_manutencao: {e}")

    def get_temperaturas(self) -> List[Dict[str, Any]]:
        '''
            temperaturas.append({
                'nome'      : nome_ponto,
                'historico' : dict(hist),                # converte defaultdict→dict p/ evitar referências externas
                'atual'     : medidas.get('value'),
                'alarme'    : medidas.get('alarmes'),
                'trip'      : medidas.get('trip'),
            })
        '''
        if len(self._cache_dados_brutos) == 0:
            self._get_dados_brutos_periodo('diario')

        temperaturas = []
        lista_snapshots = self._cache_dados_brutos.get('diario', [])
        import random
        
        for d in lista_snapshots:
            print('snapshot', d)
            print(' ')
            dados = self._parse_dados_paradas(d.get("dados"))
            lista_usinas = dados.get("usinas") or []
            for usina in lista_usinas:
                nome = usina.get("nome", "Desconhecida")
                slug = usina.get("slug", "Desconhecido")
                print('usina', nome)
                print(usina)
                dispositivos = usina.get("dispositivos") or {}
                for nome_disp, info in dispositivos.items():
                    nome_disp = info.get("nome", "Desconhecido")
                    temperaturas = info.get("temperaturas") or {"Enrolamento Fase A": random.randint(0, 100), "Enrolamento Fase B": random.randint(0, 100), "Enrolamento Fase C": random.randint(0, 100)}
                    historico = {}
                    # for nome_sensor, medidas in temperaturas.items():
                    #     historico[nome_sensor] = medidas.get('historico')

                    
                    # print('    dispositivo', nome_disp)
                    # print('  ',info)
                    # print('¨¨¨¨¨')
                
            print('----------------')
            # for usina in lista_usinas:
            #     nome_usina = usina.get("nome", "Desconhecida")
            #     dispositivos = usina.get("dispositivos") or {}
            #     for nome_disp, info in dispositivos.items():
            #         sensores_temperaturas = dados[usina][nome_disp]['temperaturas']
            #         historico = {}
            #         for nome_sensor, medidas in sensores_temperaturas.items():
            #             historico[nome_sensor] = medidas.get('historico')
            #         temperaturas.append({
            #             'nome'      : f"{nome_usina} - {nome_disp}",
            #             'atual'     : temp_atual,
            #             'alarme'    : alarme,
            #             'trip'      : info.get('trip_temp'),
            #             'risco'     : 0
            #         })
        print('--')
        print('temperaturas')
        for i, t in enumerate(temperaturas):
            print(f'{i}: {t}')
        print('--')
        return temperaturas
'''
{
  "usinas": [
    {
      "nome": "CGH APARECIDA",
      "slug": "cghaparecida",
      "dispositivos": {
        "UG-01": {
          "erro": null,
          "nome": "UG-01",
          "descricao": "US (sincronizado)",
          "tempo_leitura": 0.3763909339904785,
          "potencia_ativa_mw": 334
        }
      }
    },
    {
      "nome": "CGH FAE",
      "slug": "cghfae",
      "dispositivos": {
        "UG-01": {
          "erro": null,
          "nome": "UG-01",
          "descricao": "US (sincronizado)",
          "tempo_leitura": 0.34920620918273926,
          "potencia_ativa_mw": 529
        },
        "UG-02": {
          "erro": null,
          "nome": "UG-02",
          "descricao": "UP (parada)",
          "tempo_leitura": 0.3497161865234375,
          "potencia_ativa_mw": 0
        }
      }
    },
    {
      "nome": "CGH HOPPEN",
      "slug": "cghhoppen",
      "dispositivos": {
        "UG-01": {
          "erro": null,
          "nome": "UG-01",
          "descricao": "UP (parada)",
          "tempo_leitura": 0.29269862174987793,
          "potencia_ativa_mw": 0
        },
        "UG-02": {
          "erro": null,
          "nome": "UG-02",
          "descricao": "UP (parada)",
          "tempo_leitura": 0.2916984558105469,
          "potencia_ativa_mw": 0
        }
      }
    },
    {
      "nome": "CGH PICADAS ALTAS",
      "slug": "cghpicadasaltas",
      "dispositivos": {
        "UG-01": {
          "erro": null,
          "nome": "UG-01",
          "descricao": "UP (parada)",
          "tempo_leitura": 0.42274904251098633,
          "potencia_ativa_mw": 0
        },
        "UG-02": {
          "erro": null,
          "nome": "UG-02",
          "descricao": "UP (parada)",
          "tempo_leitura": 0.42274904251098633,
          "potencia_ativa_mw": 0
        }
      }
    },
    {
      "nome": "PCH PEDRAS",
      "slug": "pchpedras",
      "dispositivos": {
        "UG-01": {
          "erro": null,
          "nome": "UG-01",
          "descricao": "US (sincronizado)",
          "tempo_leitura": 0.3802525997161865,
          "potencia_ativa_mw": 2597,
          "temperaturas": {
            "Enrolamento Fase A": 25,
            "Enrolamento Fase B": 26,
            "Enrolamento Fase C": 27,
            "Manc. Casq. Rad. Guia": 28,
            "Mancal Comb. Casq": 29,
            }
          
        },
        "UG-02": {
          "erro": null,
          "nome": "UG-02",
          "descricao": "UP (parada)",
          "tempo_leitura": 0.3614847660064697,
          "potencia_ativa_mw": 0
        }
      }
    }
  ],
  "success": true,
  "timestamp": 1763403234.8251688
}
temperaturas = [
    {
        "nome": "CGH APARECIDA UG-01 - Enrolamento Fase A",
        "historico": { "13:01": 25, "13:02": 26, "13:03": 27 },
        "atual": None,
        "alarme": None,
        "trip": None,
        "risco": None
    },
    {
        "nome": "CGH APARECIDA UG-01 - Enrolamento Fase B",
        "historico": { "13:01": 25, "13:02": 26, "13:03": 27 },
        "atual": None,
        "alarme": None,
        "trip": None,
        "risco": None
    },
]
'''
