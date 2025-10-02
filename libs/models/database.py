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
                connection_timeout=self.connection_timeout,
                autocommit=False,
                pool_name='mypool',
                pool_size=5,
                pool_reset_session=True,
                use_pure=True
            )
            return self.connection
        except Error as e:
            raise Exception(f"Erro ao conectar ao banco de dados: {e}")

    def _cursor(self):
        if not self._is_alive():
            self.connect()
        return self.connection.cursor()

    def execute_query(self, query, params=None, retries=3):
        """Executa query com retry automático em caso de perda de conexão."""
        last_error = None
        
        for attempt in range(retries):
            try:
                # Força reconexão se não estiver viva
                if not self._is_alive():
                    if DB_DEBUG and attempt > 0:
                        print(f"[Database] 🔄 Tentando reconectar (tentativa {attempt + 1}/{retries})")
                    self.connection = None
                    self.connect()
                
                cur = self._cursor()
                try:
                    cur.execute(query, params or ())
                    self.connection.commit()
                    return cur
                except Error as e:
                    if self.connection and self.connection.is_connected():
                        self.connection.rollback()
                    raise
                finally:
                    cur.close()
                    
            except Error as e:
                last_error = e
                error_code = e.errno if hasattr(e, 'errno') else None
                connection_errors = [2006, 2013, 2055]
                
                if error_code in connection_errors and attempt < retries - 1:
                    if DB_DEBUG:
                        print(f"[Database] ⚠️ Conexão perdida (erro {error_code}), tentando novamente...")
                    self.connection = None
                    time.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    raise Exception(f"Erro ao executar query: {e}")
        
        raise Exception(f"Erro ao executar query após {retries} tentativas: {last_error}")

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

    def fetch_data(self, query, params=None, retries=3):
        """Busca dados com retry automático em caso de perda de conexão."""
        last_error = None
        
        for attempt in range(retries):
            try:
                # Força reconexão se não estiver viva
                if not self._is_alive():
                    if DB_DEBUG and attempt > 0:
                        print(f"[Database] 🔄 Tentando reconectar (tentativa {attempt + 1}/{retries})")
                    self.connection = None  # Force reset
                    self.connect()
                
                cur = self._cursor()
                try:
                    cur.execute(query, params or ())
                    result = cur.fetchall()
                    columns = [c[0] for c in cur.description]
                    return [dict(zip(columns, row)) for row in result]
                finally:
                    cur.close()
                    
            except Error as e:
                last_error = e
                error_code = e.errno if hasattr(e, 'errno') else None
                
                # Erros de conexão que devem fazer retry
                connection_errors = [2006, 2013, 2055]  # Server gone away, Lost connection, Lost connection to server at reading
                
                if error_code in connection_errors and attempt < retries - 1:
                    if DB_DEBUG:
                        print(f"[Database] ⚠️ Conexão perdida (erro {error_code}), tentando novamente...")
                    self.connection = None  # Force reset
                    time.sleep(0.5 * (attempt + 1))  # Backoff exponencial
                    continue
                else:
                    raise Exception(f"Erro ao buscar dados: {e}")
        
        raise Exception(f"Erro ao buscar dados após {retries} tentativas: {last_error}")

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