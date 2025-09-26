# libs/models/database.py
import mysql.connector
from mysql.connector import Error
import os
import time
import uuid
from threading import Lock
from dotenv import load_dotenv

load_dotenv()

DB_DEBUG = True

class _Singleton(type):
    _instance = None
    _lock = Lock()
    _created_at = None
    _uuid = None
    _create_count = 0  # quantas vezes tentou criar

    def __call__(cls, *args, **kwargs):
        cls._create_count += 1
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__call__(*args, **kwargs)
                    cls._instance = inst
                    cls._created_at = time.strftime("%Y-%m-%d %H:%M:%S")
                    cls._uuid = str(uuid.uuid4())[:8]
                    if DB_DEBUG:
                        print(f"[Database] ✅ criado (uuid={cls._uuid}, pid={os.getpid()}, created_at={cls._created_at})")
                elif DB_DEBUG:
                    print(f"[Database] ♻️ reuso após corrida (uuid={cls._uuid})")
        else:
            if DB_DEBUG:
                print(f"[Database] ♻️ reutilizando singleton (uuid={cls._uuid}, calls={cls._create_count})")
        return cls._instance

class Database(metaclass=_Singleton):  # <- troque para "object" se NÃO quiser singleton
    def __init__(self):
        self.host = os.getenv('MYSQLHOST')
        self.user = os.getenv('MYSQLUSER')
        self.password = os.getenv('MYSQLPASSWORD')
        self.database = os.getenv('MYSQLDATABASE')
        self.port = int(os.getenv('MYSQLPORT', 3306))
        self.connection_timeout = int(os.getenv('MYSQLCONNECTIONTIMEOUT', 10))
        self.connection = None

    # ---- helpers internos ----
    def _is_alive(self) -> bool:
        try:
            return self.connection is not None and self.connection.is_connected()
        except Exception:
            return False

    def connect(self):
        """Abre a conexão se necessário, senão reusa a existente."""
        if self._is_alive():
            return self.connection
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connection_timeout=self.connection_timeout
            )
            return self.connection
        except Error as e:
            raise Exception(f"Erro ao conectar ao banco de dados: {e}")

    def _cursor(self):
        if not self._is_alive():
            self.connect()
        return self.connection.cursor()

    def execute_query(self, query, params=None):
        cur = self._cursor()
        try:
            cur.execute(query, params or ())
            self.connection.commit()
            return cur
        except Error as e:
            self.connection.rollback()
            raise Exception(f"Erro ao executar query: {e}")
        finally:
            cur.close()

    def execute_many(self, queries):
        cur = self._cursor()
        try:
            for q in queries:
                if q and q.strip():
                    cur.execute(q)
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            raise Exception(f"Erro ao executar batch: {e}")
        finally:
            cur.close()

    def fetch_data(self, query, params=None):
        cur = self._cursor()
        try:
            cur.execute(query, params or ())
            result = cur.fetchall()
            columns = [c[0] for c in cur.description]
            return [dict(zip(columns, row)) for row in result]
        except Error as e:
            raise Exception(f"Erro ao buscar dados: {e}")
        finally:
            cur.close()

    def close(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Error:
            pass
        self.connection = None

    # ---- context manager ----
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        # Feche aqui se preferir ciclo curto; para manter viva, comente a linha abaixo
        # Como é singleton, normalmente deixo aberta até o processo encerrar.
        # self.close()
        pass

    # ---- fallback automático ----
    def __del__(self):
        # Garantia de fechar ao coletar o objeto / encerrar processo
        try:
            self.close()
        except Exception:
            pass