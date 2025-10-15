# libs/models/read.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, Sequence, Union, Any, Dict, List, Tuple
from libs.models.database import Database
from libs.models.utils.utils import (
    safe_ident, columns_sql, build_where_clause,
    order_sql, limit_sql,
)

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
            print('##############')
            print(' '*5,sql)
            inicio = time.time()
            dados = self.db.fetch_data(sql)
            fim = time.time() - inicio
            print(' '*5,fim)
            print('##############')
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
                "status","severidade","origem","created_at","updated_at","resolved_at"
            ],
            default_order_by="created_at",
            default_desc=True,
            db_instance=db_instance,
        )