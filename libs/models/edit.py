# libs/models/edit.py
from __future__ import annotations
from typing import Any, Dict, Optional, Sequence, Union

from libs.models.database import Database
from libs.models.utils.utils import (
    safe_ident, build_update_sql, build_set_clause, build_where_clause,
    ensure_where, ensure_data, json_param
)

Identifier = str
Columns = Union[str, Sequence[Identifier]]


class Edit:
    """
    Repositório de edição simples (parametrizado/seguro).
    - UPDATE por id
    - UPDATE por where (com os mesmos operadores do Read.where)
    """
    def __init__(self, tabela: Identifier, db_instance: Optional[Database] = None):
        self.tabela = tabela
        self.db = db_instance or Database()

    def update_by_id(self, id_: int, data: Dict[str, Any]) -> int:
        """
        Atualiza um registro pelo ID. Retorna rowcount.
        """
        data = ensure_data(data)
        try:
            self.db.connect()
            # Monta SET ...
            set_sql, set_params = build_set_clause(data)
            sql = f"UPDATE {safe_ident(self.tabela)}" + set_sql + " WHERE `id` = %s"
            params = tuple([*set_params, id_])
            cur = self.db.execute_query(sql, params)
            return cur.rowcount if cur else 0
        except Exception as e:
            self._error('Edit', 'update_by_id', e)
            return 0

    def update_where(self, where: Dict[str, Any], data: Dict[str, Any]) -> int:
        """
        Atualiza registros que satisfazem o WHERE. Retorna rowcount.
        """
        where = ensure_where(where)
        data = ensure_data(data)
        try:
            self.db.connect()
            sql, params = build_update_sql(self.tabela, data, where)
            cur = self.db.execute_query(sql, tuple(params))
            return cur.rowcount if cur else 0
        except Exception as e:
            self._error('Edit', 'update_where', e)
            return 0

    # ------------ extras úteis (opcionais) ------------

    def increment(self, where: Dict[str, Any], field: str, step: int = 1) -> int:
        """
        UPDATE ... SET `field` = `field` + step WHERE ...
        """
        where = ensure_where(where)
        if not isinstance(step, int):
            raise ValueError("step deve ser int.")
        try:
            self.db.connect()
            where_sql, where_params = build_where_clause(where)
            if not where_sql:
                raise ValueError("Condição 'where' vazia no increment.")
            sql = f"UPDATE {safe_ident(self.tabela)} SET {safe_ident(field)} = {safe_ident(field)} + %s" + where_sql
            params = tuple([step, *where_params])
            cur = self.db.execute_query(sql, params)
            return cur.rowcount if cur else 0
        except Exception as e:
            self._error('Edit', 'increment', e)
            return 0

    def set_json_key(self, where: Dict[str, Any], json_col: str, key: str, value: Any) -> int:
        """
        UPDATE ... SET `json_col` = JSON_SET(`json_col`, '$.key', %s) WHERE ...
        Cria o caminho se não existir. MySQL 5.7+ / 8+.
        """
        where = ensure_where(where)
        try:
            self.db.connect()
            where_sql, where_params = build_where_clause(where)
            if not where_sql:
                raise ValueError("Condição 'where' vazia no set_json_key.")
            # evita injection em key JSON (só alfanumérico e _)
            if not key.replace('_', '').isalnum():
                raise ValueError("Chave JSON inválida.")
            json_path = f"$.{key}"
            expr, json_str = json_param(value)
            sql = (
                f"UPDATE {safe_ident(self.tabela)} "
                f"SET {safe_ident(json_col)} = JSON_SET({safe_ident(json_col)}, %s, {expr})"
                + where_sql
            )
            params = (json_path, json_str, *where_params)
            cur = self.db.execute_query(sql, params)
            return cur.rowcount if cur else 0
        except Exception as e:
            self._error('Edit', 'set_json_key', e)
            return 0

    # ---------------------------------------------------

    def _error(self, name: str, function: str, e: Exception):
        print(f"[ERROR] Class: {name}, Function: {function}: Message: {e}")
        raise Exception(f"Erro em {name}.{function}: {e}")


# ----------------- Models "fininhos" (op_) -----------------

class OpUsinaEdit(Edit):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_usina", db_instance=db_instance)

class OpUsuarioEdit(Edit):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_usuario", db_instance=db_instance)

class OpOcorrenciaEdit(Edit):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_ocorrencia", db_instance=db_instance)
