# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _carregar_cfg_mysql → lê credenciais do .env (prefixo) e monta config do banco
# 2. _abrir_conexao_mysql → abre conexão MySQL (mysql-connector) com commit/rollback controlado
# 3. _sync_triggers_ocorrencia → desativa/recria triggers de ocorrência no destino (evita duplicar histórico)
# 4. _copiar_tabela → copia uma tabela (batch por ID) preservando colunas em comum e IDs
# 5. migrar_railway_para_local → orquestra migração Railway → Local (ordem segura por FK)
# -------------------------------------------------------------------

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

import mysql.connector
from dotenv import load_dotenv


# ---------------- CONFIGURAÇÕES / CONSTANTES ----------------

TABELAS_COPIA_ORDEM_FK = [
    "op_usina",
    "op_usuario",
    "op_ocorrencia",
    "op_ocorrencia_hist",
    "op_anexo",
    "op_paradas",
    "op_kpi_consolidado",
]

TRIGGERS_OCORRENCIA = [
    "trg_ocorrencia_after_insert",
    "trg_ocorrencia_after_update",
]

TRIGGERS_OCORRENCIA_SQL = [
    """
    CREATE TRIGGER trg_ocorrencia_after_insert
    AFTER INSERT ON op_ocorrencia
    FOR EACH ROW
    BEGIN
      INSERT INTO op_ocorrencia_hist (ocorrencia_id, usuario_id, acao, detalhe)
      VALUES (NEW.id, NEW.operador_id, 'criado',
              JSON_OBJECT('status', NEW.status));
    END;
    """,
    """
    CREATE TRIGGER trg_ocorrencia_after_update
    AFTER UPDATE ON op_ocorrencia
    FOR EACH ROW
    BEGIN
      IF (OLD.status <> NEW.status) THEN
        INSERT INTO op_ocorrencia_hist (ocorrencia_id, usuario_id, acao, detalhe)
        VALUES (NEW.id, NEW.operador_id, 'status',
                JSON_OBJECT('de', OLD.status, 'para', NEW.status));
      ELSE
        INSERT INTO op_ocorrencia_hist (ocorrencia_id, usuario_id, acao, detalhe)
        VALUES (NEW.id, NEW.operador_id, 'atualizado', NULL);
      END IF;
    END;
    """,
]


# ---------------- ERROS / WRAPPERS ----------------

class ErroMigracao(Exception):
    pass


def _falhar(etapa: str, e: Exception) -> ErroMigracao:
    return ErroMigracao(f"[MIGRACAO] {etapa}: {e}")


# ---------------- CONFIG / CONEXÃO ----------------

@dataclass(frozen=True)
class CfgMySQL:
    host: str
    port: int
    user: str
    password: str
    database: str
    ssl_disabled: bool


def _parse_bool(v: Any, default: bool = False) -> bool:
    if v is None:
        return default
    s = str(v).strip().lower()
    if s in ("1", "true", "sim", "yes", "on"):
        return True
    if s in ("0", "false", "nao", "não", "no", "off"):
        return False
    return default


def _getenv(prefixo: str, chave: str) -> Optional[str]:
    return os.getenv(f"{prefixo}{chave}") if prefixo else os.getenv(chave)


def _carregar_cfg_mysql(prefixo: str) -> CfgMySQL:
    """
    Prioridade:
      1) <prefixo>MYSQL_URL (ex: mysql://user:pass@host:3306/db)
      2) <prefixo>MYSQLHOST/MYSQLPORT/MYSQLUSER/MYSQLPASSWORD/MYSQLDATABASE
    """
    mysql_url = _getenv(prefixo, "MYSQL_URL")
    if mysql_url:
        return _cfg_mysql_por_url(prefixo, mysql_url)
    return _cfg_mysql_por_campos(prefixo)


def _cfg_mysql_por_url(prefixo: str, mysql_url: str) -> CfgMySQL:
    u = urlparse(mysql_url)
    if not u.hostname or not u.username or not u.password or not u.path:
        raise ValueError("MYSQL_URL inválida (esperado mysql://user:pass@host:port/db)")

    ssl_disabled = _parse_bool(_getenv(prefixo, "MYSQL_SSL_DISABLED"), default=False)
    return CfgMySQL(
        host=u.hostname,
        port=int(u.port or 3306),
        user=u.username,
        password=u.password,
        database=u.path.lstrip("/"),
        ssl_disabled=ssl_disabled,
    )


def _cfg_mysql_por_campos(prefixo: str) -> CfgMySQL:
    host = _getenv(prefixo, "MYSQLHOST")
    port = _getenv(prefixo, "MYSQLPORT")
    user = _getenv(prefixo, "MYSQLUSER")
    password = _getenv(prefixo, "MYSQLPASSWORD")
    database = _getenv(prefixo, "MYSQLDATABASE")
    ssl_disabled = _parse_bool(_getenv(prefixo, "MYSQL_SSL_DISABLED"), default=False)

    faltando = [k for k, v in {
        "MYSQLHOST": host,
        "MYSQLPORT": port,
        "MYSQLUSER": user,
        "MYSQLPASSWORD": password,
        "MYSQLDATABASE": database,
    }.items() if not v]
    if faltando:
        raise ValueError(f"Variáveis ausentes ({prefixo}): {', '.join(faltando)}")

    return CfgMySQL(
        host=str(host),
        port=int(port),
        user=str(user),
        password=str(password),
        database=str(database),
        ssl_disabled=ssl_disabled,
    )


class ConexaoMySQL:
    def __init__(self, cfg: CfgMySQL):
        self.cfg = cfg
        self.conn = None

    def open(self) -> "ConexaoMySQL":
        self.conn = mysql.connector.connect(
            host=self.cfg.host,
            port=self.cfg.port,
            user=self.cfg.user,
            password=self.cfg.password,
            database=self.cfg.database,
            autocommit=False,
            ssl_disabled=self.cfg.ssl_disabled,
        )
        return self

    def close(self) -> None:
        try:
            if self.conn:
                self.conn.close()
        finally:
            self.conn = None

    def fetchall(self, sql: str, params: Tuple[Any, ...] = ()) -> List[Tuple[Any, ...]]:
        cur = self._cursor()
        try:
            cur.execute(sql, params)
            return list(cur.fetchall() or [])
        finally:
            cur.close()

    def execute(self, sql: str, params: Tuple[Any, ...] = ()) -> None:
        cur = self._cursor()
        try:
            cur.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def executemany(self, sql: str, rows: Sequence[Tuple[Any, ...]]) -> None:
        if not rows:
            return
        cur = self._cursor()
        try:
            cur.executemany(sql, rows)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def scalar(self, sql: str, params: Tuple[Any, ...] = ()) -> int:
        rows = self.fetchall(sql, params)
        if not rows or rows[0] is None or rows[0][0] is None:
            return 0
        return int(rows[0][0])

    def _cursor(self):
        if not self.conn:
            raise RuntimeError("Conexão não aberta.")
        return self.conn.cursor()


# ---------------- SQL HELPERS ----------------

_VALID_IDENT = re.compile(r"^[A-Za-z0-9_]+$")


def _qi(nome: str) -> str:
    if not _VALID_IDENT.match(nome or ""):
        raise ValueError(f"Identificador inválido: {nome!r}")
    return f"`{nome}`"


def _colunas_tabela(db: ConexaoMySQL, tabela: str) -> List[str]:
    rows = db.fetchall(f"SHOW COLUMNS FROM {_qi(tabela)}")
    return [str(r[0]) for r in rows]


def _colunas_comuns(db_src: ConexaoMySQL, db_dst: ConexaoMySQL, tabela: str) -> List[str]:
    src = set(_colunas_tabela(db_src, tabela))
    dst = _colunas_tabela(db_dst, tabela)
    return [c for c in dst if c in src]


def _sql_insert(tabela: str, colunas: List[str]) -> str:
    cols = ", ".join(_qi(c) for c in colunas)
    ph = ", ".join(["%s"] * len(colunas))
    return f"INSERT INTO {_qi(tabela)} ({cols}) VALUES ({ph})"


def _sql_select_por_id(tabela: str, colunas: List[str]) -> str:
    cols = ", ".join(_qi(c) for c in colunas)
    return f"SELECT {cols} FROM {_qi(tabela)} WHERE `id` > %s ORDER BY `id` ASC LIMIT %s"


# ---------------- TRIGGERS ----------------

def _sync_triggers_ocorrencia(db_dst: ConexaoMySQL, habilitar: bool) -> None:
    if habilitar:
        for sql in TRIGGERS_OCORRENCIA_SQL:
            db_dst.execute(sql)
        return

    for trg in TRIGGERS_OCORRENCIA:
        db_dst.execute(f"DROP TRIGGER IF EXISTS {_qi(trg)}")


# ---------------- CÓPIA ----------------

def _limpar_destino(db_dst: ConexaoMySQL, tabelas: List[str]) -> None:
    db_dst.execute("SET FOREIGN_KEY_CHECKS = 0")
    try:
        for tabela in reversed(tabelas):
            db_dst.execute(f"TRUNCATE TABLE {_qi(tabela)}")
    finally:
        db_dst.execute("SET FOREIGN_KEY_CHECKS = 1")


def _copiar_tabela(db_src: ConexaoMySQL, db_dst: ConexaoMySQL, tabela: str, batch: int) -> int:
    colunas = _colunas_comuns(db_src, db_dst, tabela)
    if not colunas:
        return 0
    if "id" not in colunas:
        raise ValueError(f"Tabela sem coluna 'id' (não suportado): {tabela}")

    idx_id = colunas.index("id")
    sql_sel = _sql_select_por_id(tabela, colunas)
    sql_ins = _sql_insert(tabela, colunas)

    total = 0
    last_id = 0
    while True:
        rows = db_src.fetchall(sql_sel, (last_id, int(batch)))
        if not rows:
            return total
        db_dst.executemany(sql_ins, rows)
        total += len(rows)
        last_id = int(rows[-1][idx_id])


# ---------------- ORQUESTRAÇÃO ----------------

def migrar_railway_para_local(
    prefixo_railway: str = "RAILWAY_",
    prefixo_local: str = "",
    batch: int = 1000,
    limpar_destino: bool = False,
) -> None:
    load_dotenv()

    cfg_src = _carregar_cfg_mysql(prefixo_railway)
    cfg_dst = _carregar_cfg_mysql(prefixo_local)

    db_src = ConexaoMySQL(cfg_src).open()
    db_dst = ConexaoMySQL(cfg_dst).open()
    try:
        if limpar_destino:
            print("[MIGRACAO] Limpando destino...")
            _sync_triggers_ocorrencia(db_dst, habilitar=False)
            _limpar_destino(db_dst, TABELAS_COPIA_ORDEM_FK)
            _sync_triggers_ocorrencia(db_dst, habilitar=True)

        # Evita duplicação do op_ocorrencia_hist durante import do op_ocorrencia
        print("[MIGRACAO] Desativando triggers de ocorrência no destino...")
        _sync_triggers_ocorrencia(db_dst, habilitar=False)

        for tabela in TABELAS_COPIA_ORDEM_FK:
            print(f"[MIGRACAO] Copiando {tabela}...")
            total = _copiar_tabela(db_src, db_dst, tabela, batch=batch)
            print(f"[MIGRACAO] {tabela}: {total} linhas")

        print("[MIGRACAO] Recriando triggers de ocorrência no destino...")
        _sync_triggers_ocorrencia(db_dst, habilitar=True)

        print("[MIGRACAO] ✅ Concluído.")

    except Exception as e:
        raise _falhar("migrar_railway_para_local", e) from e
    finally:
        db_src.close()
        db_dst.close()


def _parse_args(argv: Sequence[str]) -> dict:
    args = set(argv or [])
    return {
        "limpar_destino": ("--limpar-destino" in args) or ("--truncate" in args),
    }


if __name__ == "__main__":
    try:
        opts = _parse_args(os.sys.argv[1:])
        migrar_railway_para_local(limpar_destino=bool(opts["limpar_destino"]))
    except Exception as e:
        print(str(e))
        raise


