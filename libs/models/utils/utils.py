# libs/models/utils.py
from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import re
import unicodedata
import json

Identifier = str
Columns = Union[str, Sequence[Identifier]]

# Identificadores simples (sem schema/pontos)
_VALID_IDENT = re.compile(r"^[A-Za-z0-9_]+$")

# caracteres “neutros” removidos SÓ para COMPARAÇÃO (nunca para salvar/mostrar na UI)
NORMALIZE_STRIP_CHARS = " -_"

# ---------------- Identifiers / Columns ----------------
def safe_ident(name: str) -> str:
    """Valida e quote um identificador simples (coluna/tabela)."""
    if not isinstance(name, str) or not _VALID_IDENT.match(name):
        raise ValueError(f"Identificador inválido: {name!r}")
    return f"`{name}`"

def columns_sql(cols: Optional[Columns]) -> str:
    """Monta a lista de colunas para SELECT."""
    if cols in (None, "*"):
        return "*"
    if isinstance(cols, (list, tuple)):
        if not cols:
            return "*"
        return ", ".join(safe_ident(c) for c in cols)
    raise TypeError("colunas deve ser '*', None ou sequência de strings.")

# ---------------- Normalização para busca/comparação ----------------
def _strip_chars_sql(expr: str, chars: str = NORMALIZE_STRIP_CHARS) -> str:
    """Gera REPLACE encadeado para remover chars no SQL."""
    for ch in chars:
        expr = f"REPLACE({expr}, '{ch}', '')"
    return expr

def norm_sql_expr(col_quoted: str, lower: bool = True, collate: str = "utf8mb4_0900_ai_ci") -> str:
    """
    Expressão SQL normalizada (comparação):
      - remove espaços/hífens/sublinhados
      - LOWER
      - collation acento/maiúscula-insensível
    """
    expr = _strip_chars_sql(col_quoted)
    if lower:
        expr = f"LOWER({expr})"
    if collate:
        expr = f"{expr} COLLATE {collate}"
    return expr

def normalize_for_search(value: Any, strip_chars: str = NORMALIZE_STRIP_CHARS, to_lower: bool = True) -> str:
    """Normaliza em Python: remove acentos e chars neutros; lower opcional."""
    s = "" if value is None else str(value)
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    for ch in strip_chars:
        s = s.replace(ch, '')
    return s.lower() if to_lower else s

def like_contains(v: str) -> str:    return f"%{v}%"
def like_startswith(v: str) -> str:  return f"{v}%"
def like_endswith(v: str) -> str:    return f"%{v}"

# ---------------- ORDER / LIMIT ----------------
def order_sql(order_by: Optional[str], desc: bool) -> str:
    if not order_by:
        return ""
    return f" ORDER BY {safe_ident(order_by)} {'DESC' if desc else 'ASC'} "

def limit_sql(limit: Optional[int], offset: Optional[int]) -> str:
    parts: List[str] = []
    if isinstance(limit, int) and limit > 0:
        parts.append(f" LIMIT {limit} ")
        if isinstance(offset, int) and offset >= 0:
            parts.append(f" OFFSET {offset} ")
    return "".join(parts)

# ---------------- WHERE builder ----------------
def build_where_clause(where: Dict[str, Any]) -> Tuple[str, List[Any]]:
    """
    where: {col: valor} -> '='
           {col: ('in', [1,2,3])}
           {col: ('like', '%texto%')}
           {col: ('like_norm', '%texto%')}        # normaliza col e valor
           {col: ('eq_norm', 'Texto')}
           {col: ('startswith_norm', 'Texto')}
           {col: ('endswith_norm', 'Texto')}
           {col: ('ne', valor)}                   # !=
           {col: ('gt'|'gte'|'lt'|'lte', valor)}
           {col: ('regexp', 'padrão')}
    Retorna: (" WHERE ...", [params])
    """
    if not where:
        return "", []  # <-- IMPORTANTÍSSIMO: sempre retorne tuple

    parts: List[str] = []
    params: List[Any] = []

    for key, val in where.items():
        col = safe_ident(key)

        if isinstance(val, tuple) and val:
            op = str(val[0]).lower()
            arg = val[1] if len(val) > 1 else None

            if op == "in":
                seq = list(arg) if isinstance(arg, (list, tuple, set)) else [arg]
                if not seq:
                    parts.append("1=0")
                else:
                    placeholders = ", ".join(["%s"] * len(seq))
                    parts.append(f"{col} IN ({placeholders})")
                    params.extend(seq)

            elif op == "like":
                parts.append(f"{col} LIKE %s")
                params.append(arg)

            elif op == "like_norm":
                expr = norm_sql_expr(col)
                parts.append(f"{expr} LIKE %s")
                params.append(normalize_for_search(arg))

            elif op == "eq_norm":
                expr = norm_sql_expr(col)
                parts.append(f"{expr} = %s")
                params.append(normalize_for_search(arg))

            elif op == "startswith_norm":
                expr = norm_sql_expr(col)
                parts.append(f"{expr} LIKE %s")
                params.append(like_startswith(normalize_for_search(arg)))

            elif op == "endswith_norm":
                expr = norm_sql_expr(col)
                parts.append(f"{expr} LIKE %s")
                params.append(like_endswith(normalize_for_search(arg)))

            elif op == "ne":
                parts.append(f"{col} <> %s")
                params.append(arg)

            elif op in ("gt", "gte", "lt", "lte"):
                cmp_map = {"gt": ">", "gte": ">=", "lt": "<", "lte": "<="}
                parts.append(f"{col} {cmp_map[op]} %s")
                params.append(arg)

            elif op == "regexp":
                parts.append(f"{col} REGEXP %s")
                params.append(arg)

            else:
                raise ValueError(f"Operador desconhecido em where: {op}")

        else:
            parts.append(f"{col} = %s")
            params.append(val)

    clause = " WHERE " + " AND ".join(parts)
    return clause, params  # <-- IMPORTANTÍSSIMO
# ---------------- FIM utils ----------------

def build_set_clause(data: Dict[str, Any]) -> tuple[str, list[Any]]:
    """
    Gera ' SET `col1`=%s, `col2`=%s ...' e os params na mesma ordem.
    """
    if not data:
        raise ValueError("SET vazio não é permitido.")
    parts: List[str] = []
    params: List[Any] = []
    for k, v in data.items():
        parts.append(f"{safe_ident(k)} = %s")
        params.append(v)
    return " SET " + ", ".join(parts), params

def build_update_sql(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> tuple[str, list[Any]]:
    """
    UPDATE `table` SET ... WHERE ...
    Retorna (sql, params) com parâmetros do SET seguidos dos do WHERE.
    """
    set_sql, set_params = build_set_clause(data)
    where_sql, where_params = build_where_clause(where)
    if not where_sql:
        # proteção contra UPDATE full table acidental
        raise ValueError("Condição 'where' vazia em UPDATE.")
    sql = f"UPDATE {safe_ident(table)}" + set_sql + where_sql
    return sql, [*set_params, *where_params]

# (Opcional) helpers práticos
def ensure_where(where: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not where:
        raise ValueError("Condição 'where' não pode ser vazia.")
    return where

def ensure_data(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not data:
        raise ValueError("Dados de atualização (data) não podem ser vazios.")
    return data

def json_param(value: Any) -> Tuple[str, str]:
    """
    Retorna a expressão SQL e o parâmetro serializado para JSON.
    Usa %s (paramstyle do mysql-connector).
    """
    # Opção A (CAST): funciona bem no MySQL 8/5.7 recentes
    return "CAST(%s AS JSON)", json.dumps(value, ensure_ascii=False)

    # OU, se preferir máxima compatibilidade:
    # return "JSON_EXTRACT(%s, '$')", json.dumps(value, ensure_ascii=False)

def desempenho(func):
    import time
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} - Tempo de execução: {end_time - start_time} segundos")
        print('-' * 50)
        return result
    return wrapper
