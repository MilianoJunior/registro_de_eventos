# libs/models/delete.py
from __future__ import annotations
from typing import Any, Dict, Optional
from libs.models.database import Database
from libs.models.utils.utils import safe_ident, build_where_clause, ensure_where


class Delete:
    """
    Repositório de exclusão simples (parametrizado/seguro).
    - DELETE por id
    - DELETE por where (com os mesmos operadores do Read.where)
    """
    def __init__(self, tabela: str, db_instance: Optional[Database] = None):
        self.tabela = tabela
        self.db = db_instance or Database()

    def delete_by_id(self, id_: int) -> int:
        """
        Deleta um registro pelo ID. Retorna rowcount.
        """
        try:
            self.db.connect()
            sql = f"DELETE FROM {safe_ident(self.tabela)} WHERE `id` = %s"
            cur = self.db.execute_query(sql, (id_,))
            return cur.rowcount if cur else 0
        except Exception as e:
            self._error('Delete', 'delete_by_id', e)
            return 0

    def delete_where(self, where: Dict[str, Any]) -> int:
        """
        Deleta registros que satisfazem o WHERE. Retorna rowcount.
        """
        where = ensure_where(where)
        try:
            self.db.connect()
            where_sql, where_params = build_where_clause(where)
            if not where_sql:
                raise ValueError("Condição 'where' vazia no delete_where.")
            sql = f"DELETE FROM {safe_ident(self.tabela)}" + where_sql
            cur = self.db.execute_query(sql, tuple(where_params))
            return cur.rowcount if cur else 0
        except Exception as e:
            self._error('Delete', 'delete_where', e)
            return 0

    def _error(self, name: str, function: str, e: Exception):
        print(f"[ERROR] Class: {name}, Function: {function}: Message: {e}")
        raise Exception(f"Erro em {name}.{function}: {e}")


# ----------------- Models "fininhos" (op_) -----------------

class OpUsinaDelete(Delete):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_usina", db_instance=db_instance)

class OpUsuarioDelete(Delete):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_usuario", db_instance=db_instance)

class OpOcorrenciaDelete(Delete):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_ocorrencia", db_instance=db_instance)

class OpParadasDelete(Delete):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_paradas", db_instance=db_instance)

