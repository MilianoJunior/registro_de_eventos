'''
Considerando o prompt:


User
Como posso tornar o código com um menor numero de linhas e mantendo a funcionalidade, esse código está acoplado em um projeto maior, suas alterações apenas serão copiadas e coladas e o código não pode gerar erro:

passei o código original...

As respostas foram:

Código original:
366 - 125 = 241

Código revisado gemini 3 pro:
110 - 9 = 101

Código revisado kimi:
229 - 115 = 114

Código revisado codex:
495 - 231 = 264
'''

# gemini 3 pro
class OpOcorrencia(BaseReader):
    tabela, colunas_padrao, order_padrao, desc_padrao = "op_ocorrencia", ["id", "usina_id", "operador_id", "tipo", "categoria", "unidade", "tags", "playbook", "template_texto", "descricao", "status", "severidade", "origem", "metadata", "created_at", "updated_at", "resolved_at", "requer_acao", "data_ocorrencia", "resolvida_por", "resolucao_descricao"], "created_at", True

    @desempenho
    def convert_id_to_name(self, id: int) -> str:
        return {"1": "CGH APARECIDA", "2": "CGH FAE", "3": "CGH HOPPEN", "4": "CGH PICADAS ALTAS", "5": "PCH PEDRAS"}.get(str(id), "N/A")

    def _injetar_usina_nome(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for r in (rows or []):
            if isinstance(r, dict) and "usina_nome" not in r: r["usina_nome"] = self.convert_id_to_name(r.get("usina_id"))
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
        return self._injetar_usina_nome(self._run(f"SELECT * FROM {self.tabela} WHERE requer_acao = 1 ORDER BY created_at DESC LIMIT 200"))

    @desempenho
    def listar_usina_por_periodo(self, usina_id: int, data_inicio: Optional[datetime] = None, data_fim: Optional[datetime] = None, limit: int = 30) -> List[Dict[str, Any]]:
        conds, params = [f"{safe_ident('usina_id')} = %s"], [usina_id]
        if data_inicio: conds.append(f"{safe_ident('created_at')} >= %s"); params.append(data_inicio)
        if data_fim: conds.append(f"{safe_ident('created_at')} <= %s"); params.append(data_fim)
        sql = f"SELECT {columns_sql(self.colunas_padrao)} FROM {safe_ident(self.tabela)} WHERE {' AND '.join(conds)} ORDER BY {safe_ident('created_at')} DESC LIMIT %s"
        return self._injetar_usina_nome(self._run(sql, tuple(params + [int(limit)])))

    @desempenho
    def get_counts_by_status(self) -> Dict[str, int]:
        rows = self._run(f"SELECT status, COUNT(*) AS total FROM {safe_ident(self.tabela)} GROUP BY status")
        return {r["status"]: r["total"] for r in rows} if rows else {}

    @desempenho
    def get_open_actions(self, limit: int = 20) -> List[Dict]:
        return self.where_eq(where={"requer_acao": 1, "resolvida_por": ("IS NULL", None)}, order_by="created_at", desc=True, limit=limit)

    @desempenho
    def listar_api(self, status_list: Optional[List[str]] = None, requer_acao: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        where = {}
        if status_list: where["status"] = status_list[0] if len(status_list) == 1 else ("IN", tuple(status_list))
        if requer_acao is not None: where["requer_acao"] = requer_acao
        return self._injetar_usina_nome(self.where_eq(where=where, order_by="created_at", desc=True, limit=limit))


class OpParadas(BaseReader):
    tabela, colunas_padrao, order_padrao, desc_padrao = "op_paradas", ["id", "timestamp", "dados"], "timestamp", True

    def __init__(self, db: Optional[Database] = None):
        super().__init__(db); self._cache_dados_brutos = {}

    def _parse_dados_paradas(self, raw: Any) -> Optional[Dict[str, Any]]:
        try: return raw if isinstance(raw, dict) else (json.loads(raw) if isinstance(raw, str) else None)
        except Exception: return None

    def _is_manutencao(self, s: Any) -> bool: # Helper unificado
        return "manutencao" in (str(s).lower().replace("ç", "c") if s else "")

    def _acumular_manutencao_por_usina(self, totais, estado_anterior, lista_usinas, dt_min):
        for usina in (lista_usinas or []):
            if not (slug := usina.get("slug")) or not isinstance(disp := usina.get("dispositivos"), dict): continue
            if slug not in estado_anterior: estado_anterior[slug] = {}
            if slug not in totais: totais[slug] = {"tempo_manutencao": 0.0, "eventos": 0.0}
            for nome, info in disp.items():
                if isinstance(info, dict) and (em_manut := self._is_manutencao(info.get("descricao"))):
                    totais[slug]["tempo_manutencao"] += dt_min
                    if not estado_anterior[slug].get(nome, False): totais[slug]["eventos"] += 1.0
                estado_anterior[slug][nome] = em_manut if isinstance(info, dict) else False

    def _formatar_mttr(self, total: float, ev: float) -> str:
        h, m = divmod((total / ev) if ev > 0 else total, 60)
        return f"{int(h)}h {int(m)}m" if h > 0 else f"{int(m)} min" if (h*60 + m) > 0 else "0 min"

    def _get_dados_brutos_periodo(self, periodo: str) -> List[Dict[str, Any]]:
        data = self._run("SELECT timestamp, dados FROM op_paradas WHERE timestamp >= %s ORDER BY timestamp ASC", (_periodo_para_intervalo(periodo),))
        self._cache_dados_brutos[periodo] = data; return data

    def _get_ultimos_dados_brutos(self, limit: int = 10) -> List[Dict[str, Any]]:
        return sorted(self._run("SELECT timestamp, dados FROM op_paradas ORDER BY id DESC LIMIT %s", (limit,)), key=lambda x: x['timestamp'])

    @desempenho
    def get_indicadores_manutencao(self, periodo: str = 'diario') -> Dict[str, Any]:
        try:
            rows, estado_anterior, totais = self._get_dados_brutos_periodo(periodo), {}, {}
            for ant, atual in zip(rows, rows[1:]):
                if not (isinstance(ts0 := ant.get("timestamp"), datetime) and isinstance(ts1 := atual.get("timestamp"), datetime)): continue
                if 0 < (dt := (ts1 - ts0).total_seconds() / 60.0) <= 60.0 and self._is_manutencao(raw := ant.get("dados")):
                    if dados := self._parse_dados_paradas(raw): self._acumular_manutencao_por_usina(totais, estado_anterior, dados.get("usinas"), dt)
            return {s: {"mttr_str": self._formatar_mttr(t["tempo_manutencao"], t["eventos"])} for s, t in totais.items()}
        except Exception as e: raise Exception(f"Erro em get_indicadores_manutencao: {e}")

# Kimi 2.5
class OpOcorrencia(BaseReader):
    tabela = "op_ocorrencia"
    colunas_padrao = ["id", "usina_id", "operador_id", "tipo", "categoria", "unidade", "tags", "playbook", "template_texto", "descricao", "status", "severidade", "origem", "metadata", "created_at", "updated_at", "resolved_at", "requer_acao", "data_ocorrencia", "resolvida_por", "resolucao_descricao"]
    order_padrao = "created_at"
    desc_padrao = True
    USINAS = {1: "CGH APARECIDA", 2: "CGH FAE", 3: "CGH HOPPEN", 4: "CGH PICADAS ALTAS", 5: "PCH PEDRAS"}

    @desempenho
    def convert_id_to_name(self, id: int) -> str:
        return self.USINAS.get(id, "N/A")

    def _injetar_usina_nome(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [r.update(usina_nome=self.convert_id_to_name(r.get("usina_id"))) or r for r in rows or [] if isinstance(r, dict)]

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
        return self._injetar_usina_nome(self.where_eq(where={"requer_acao": 1}, order_by="created_at", desc=True, limit=200))

    @desempenho
    def listar_usina_por_periodo(self, usina_id: int, data_inicio: Optional[datetime] = None, data_fim: Optional[datetime] = None, limit: int = 30) -> List[Dict[str, Any]]:
        cols, params = columns_sql(self.colunas_padrao), [usina_id]
        sql = f"SELECT {cols} FROM {safe_ident(self.tabela)} WHERE {safe_ident('usina_id')} = %s"
        for dt, op in [(data_inicio, ">="), (data_fim, "<=")]:
            if dt:
                sql += f" AND {safe_ident('created_at')} {op} %s"
                params.append(dt)
        return self._injetar_usina_nome(self._run(f"{sql} ORDER BY {safe_ident('created_at')} DESC LIMIT %s", tuple(params + [int(limit)])))

    @desempenho
    def get_counts_by_status(self) -> Dict[str, int]:
        return {r["status"]: r["total"] for r in self._run(f"SELECT status, COUNT(*) AS total FROM {safe_ident(self.tabela)} GROUP BY status") or []}

    @desempenho
    def get_open_actions(self, limit: int = 20) -> List[Dict]:
        return self.where_eq(where={"requer_acao": 1, "resolvida_por": ("IS NULL", None)}, order_by="created_at", desc=True, limit=limit)

    @desempenho
    def listar_api(self, status_list: Optional[List[str]] = None, requer_acao: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        where = {"status": status_list[0] if status_list and len(status_list) == 1 else ("IN", tuple(status_list)) if status_list else None}
        where = {k: v for k, v in {**where, "requer_acao": requer_acao}.items() if v is not None}
        return self._injetar_usina_nome(self.where_eq(where=where, order_by="created_at", desc=True, limit=limit))


class OpParadas(BaseReader):
    tabela = "op_paradas"
    colunas_padrao = ["id", "timestamp", "dados"]
    order_padrao = "timestamp"
    desc_padrao = True

    def __init__(self, db: Optional[Database] = None):
        super().__init__(db)
        self._cache_dados_brutos: Dict[str, List[Dict[str, Any]]] = {}

    def _parse_dados_paradas(self, raw: Any) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(raw) if isinstance(raw, str) else raw if isinstance(raw, dict) else None
        except:
            return None

    def _descricao_indica_manutencao(self, descricao: str) -> bool:
        return "manut" in (descricao or "").lower()

    def _payload_pode_conter_manutencao(self, raw: Any) -> bool:
        return True if not isinstance(raw, str) else "manut" in raw.lower()

    def _acumular_manutencao_por_usina(self, totais: Dict[str, Dict[str, float]], estado_anterior: Dict[str, Dict[str, bool]], lista_usinas: List[Dict[str, Any]], dt_minutos: float) -> None:
        for usina in lista_usinas or []:
            if not (slug := usina.get("slug")) or not isinstance(dispositivos := usina.get("dispositivos"), dict):
                continue
            estado_anterior.setdefault(slug, {})
            totais.setdefault(slug, {"tempo_manutencao": 0.0, "eventos": 0.0})
            for nome_disp, info in dispositivos.items():
                if isinstance(info, dict) and (em_manut := self._descricao_indica_manutencao(info.get("descricao") or "")):
                    totais[slug]["tempo_manutencao"] += float(dt_minutos)
                    totais[slug]["eventos"] += not estado_anterior[slug].get(nome_disp, False)
                    estado_anterior[slug][nome_disp] = True

    def _formatar_mttr(self, tempo_total_min: float, eventos: float) -> str:
        m = (tempo_total_min / eventos) if eventos > 0 else tempo_total_min
        return f"{int(m // 60)}h {int(m % 60)}m" if m > 60 else f"{int(m)} min" if m > 0 else "0 min"

    def _get_dados_brutos_periodo(self, periodo: str) -> List[Dict[str, Any]]:
        self._cache_dados_brutos[periodo] = self._run("SELECT timestamp, dados FROM op_paradas WHERE timestamp >= %s ORDER BY timestamp ASC", (_periodo_para_intervalo(periodo),))
        return self._cache_dados_brutos[periodo]

    def _get_ultimos_dados_brutos(self, limit: int = 10) -> List[Dict[str, Any]]:
        return sorted(self._run("SELECT timestamp, dados FROM op_paradas ORDER BY id DESC LIMIT %s", (limit,)), key=lambda x: x['timestamp'])

    @desempenho
    def get_indicadores_manutencao(self, periodo: str = 'diario') -> Dict[str, Any]:
        try:
            estado_anterior, totais, anterior = {}, {}, None
            for atual in self._get_dados_brutos_periodo(periodo):
                if anterior and isinstance(ts_ant := anterior.get("timestamp"), datetime) and isinstance(ts_atual := atual.get("timestamp"), datetime) and 0 < (dt_minutos := (ts_atual - ts_ant).total_seconds() / 60.0) <= 60.0 and (raw := anterior.get("dados")) and self._payload_pode_conter_manutencao(raw) and (dados := self._parse_dados_paradas(raw)) and isinstance(lista_usinas := dados.get("usinas"), list):
                    self._acumular_manutencao_por_usina(totais, estado_anterior, lista_usinas, dt_minutos)
                anterior = atual
            return {slug: {"mttr_str": self._formatar_mttr(t["tempo_manutencao"], t["eventos"])} for slug, t in totais.items()}
        except Exception as e:
            raise Exception(f"Erro em get_indicadores_manutencao: {e}")

# codex

class OpOcorrencia(BaseReader):
    tabela = "op_ocorrencia"
    colunas_padrao = [
        "id",
        "usina_id",
        "operador_id",
        "tipo",
        "categoria",
        "unidade",
        "tags",
        "playbook",
        "template_texto",
        "descricao",
        "status",
        "severidade",
        "origem",
        "metadata",
        "created_at",
        "updated_at",
        "resolved_at",
        "requer_acao",
        "data_ocorrencia",
        "resolvida_por",
        "resolucao_descricao",
    ]
    order_padrao = "created_at"
    desc_padrao = True
    USINAS = {
        "1": "CGH APARECIDA",
        "2": "CGH FAE",
        "3": "CGH HOPPEN",
        "4": "CGH PICADAS ALTAS",
        "5": "PCH PEDRAS",
    }

    @desempenho
    def convert_id_to_name(self, id: int) -> str:
        return self.USINAS.get(str(id), "N/A")

    def _injetar_usina_nome(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for r in rows or []:
            if isinstance(r, dict) and "usina_nome" not in r:
                r["usina_nome"] = self.convert_id_to_name(r.get("usina_id"))
        return rows

    def _listar(
        self,
        where: Dict[str, Any],
        order_by: str = "id",
        desc: bool = True,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        return self._injetar_usina_nome(
            self.where_eq(where=where, order_by=order_by, desc=desc, limit=limit)
        )

    @desempenho
    def listar_recentes_por_id(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._listar({}, limit=limit)

    @desempenho
    def listar_novas_por_id(self, ultimo_id: int, limit: int = 200) -> List[Dict[str, Any]]:
        return self._listar({"id": (">", ultimo_id)}, limit=limit)

    @desempenho
    def listar_recentes_usina_por_id(self, usina_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        return self._listar({"usina_id": usina_id}, limit=limit)

    @desempenho
    def listar_novas_usina_por_id(
        self, usina_id: int, ultimo_id: int, limit: int = 200
    ) -> List[Dict[str, Any]]:
        return self._listar({"usina_id": usina_id, "id": (">", ultimo_id)}, limit=limit)

    @desempenho
    def listar_requer_acao(self) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {self.tabela} WHERE requer_acao = 1 ORDER BY created_at DESC LIMIT 200"
        return self._injetar_usina_nome(self._run(sql))

    @desempenho
    def listar_usina_por_periodo(
        self,
        usina_id: int,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        cols = columns_sql(self.colunas_padrao)
        conds = [f"{safe_ident('usina_id')} = %s"]
        params: List[Any] = [usina_id]
        if data_inicio:
            conds.append(f"{safe_ident('created_at')} >= %s")
            params.append(data_inicio)
        if data_fim:
            conds.append(f"{safe_ident('created_at')} <= %s")
            params.append(data_fim)
        sql = (
            f"SELECT {cols} FROM {safe_ident(self.tabela)} WHERE "
            f"{' AND '.join(conds)} ORDER BY {safe_ident('created_at')} DESC LIMIT %s"
        )
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
            limit=limit,
        )

    @desempenho
    def listar_api(
        self,
        status_list: Optional[List[str]] = None,
        requer_acao: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        where: Dict[str, Any] = {}
        if status_list:
            where["status"] = (
                status_list[0] if len(status_list) == 1 else ("IN", tuple(status_list))
            )
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
        return "manutenção" in desc or "manutencao" in desc

    def _payload_pode_conter_manutencao(self, raw: Any) -> bool:
        if isinstance(raw, str):
            s = raw.lower()
            return "manutencao" in s or "manutenção" in s
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
            estado_anterior.setdefault(slug, {})
            totais.setdefault(slug, {"tempo_manutencao": 0.0, "eventos": 0.0})
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
        horas, minutos = divmod(int(mttr_min), 60)
        return f"{horas}h {minutos}m" if horas > 0 else f"{minutos} min"

    def _get_dados_brutos_periodo(self, periodo: str) -> List[Dict[str, Any]]:
        janela = _periodo_para_intervalo(periodo)
        sql = (
            "SELECT timestamp, dados FROM op_paradas "
            "WHERE timestamp >= %s ORDER BY timestamp ASC"
        )
        data = self._run(sql, (janela,))
        self._cache_dados_brutos[periodo] = data
        return data

    def _get_ultimos_dados_brutos(self, limit: int = 10) -> List[Dict[str, Any]]:
        sql = "SELECT timestamp, dados FROM op_paradas ORDER BY id DESC LIMIT %s"
        data = self._run(sql, (limit,))
        return sorted(data, key=lambda x: x["timestamp"])

    @desempenho
    def get_indicadores_manutencao(self, periodo: str = "diario") -> Dict[str, Any]:
        try:
            rows = self._get_dados_brutos_periodo(periodo)
            estado_anterior: Dict[str, Dict[str, bool]] = {}
            totais: Dict[str, Dict[str, float]] = {}
            anterior: Optional[Dict[str, Any]] = None
            for atual in rows:
                if anterior is None:
                    anterior = atual
                    continue
                ts_ant, ts_atual = anterior.get("timestamp"), atual.get("timestamp")
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
                    self._acumular_manutencao_por_usina(
                        totais, estado_anterior, lista_usinas, dt_minutos
                    )
                anterior = atual
            return {
                slug: {"mttr_str": self._formatar_mttr(t["tempo_manutencao"], t["eventos"])}
                for slug, t in totais.items()
            }
        except Exception as e:
            raise Exception(f"Erro em get_indicadores_manutencao: {e}")
