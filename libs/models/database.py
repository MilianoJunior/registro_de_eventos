# libs/models/database.py
import mysql.connector
from mysql.connector import Error, pooling
import os
import time
import uuid
from threading import Lock
from dotenv import load_dotenv

load_dotenv()

DB_DEBUG = True

# ============================================================
# CONNECTION POOL (Singleton Global)
# ============================================================
_connection_pool = None
_pool_lock = Lock()

def get_connection_pool():
    """Retorna o pool de conexões (singleton)"""
    global _connection_pool
    
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                try:
                    pool_config = {
                        'pool_name': 'mypool',
                        'pool_size': int(os.getenv('MYSQL_POOL_SIZE', 10)),
                        'pool_reset_session': True,
                        'host': os.getenv('MYSQLHOST'),
                        'user': os.getenv('MYSQLUSER'),
                        'password': os.getenv('MYSQLPASSWORD'),
                        'database': os.getenv('MYSQLDATABASE'),
                        'port': int(os.getenv('MYSQLPORT', 3306)),
                        'connect_timeout': int(os.getenv('MYSQLCONNECTIONTIMEOUT', 10)),
                        'autocommit': False,
                        'use_pure': True
                    }
                    
                    _connection_pool = pooling.MySQLConnectionPool(**pool_config)
                    
                    if DB_DEBUG:
                        print(f"[ConnectionPool] ✅ Pool criado com {pool_config['pool_size']} conexões")
                        
                except Error as e:
                    raise Exception(f"Erro ao criar connection pool: {e}")
    
    return _connection_pool

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
        self.pool = get_connection_pool()  # Pool global
        self.connection = None  # Conexão atual do request

    # ---- helpers internos ----
    def _is_alive(self) -> bool:
        try:
            return self.connection is not None and self.connection.is_connected()
        except Exception:
            return False

    def connect(self):
        """Obtém uma conexão do pool."""
        if self._is_alive():
            return self.connection
        try:
            start_time = time.time()
            self.connection = self.pool.get_connection()
            
            if DB_DEBUG:
                elapsed = time.time() - start_time
                print(f"[Database] 🔌 Conexão obtida do pool em {elapsed:.4f}s")
            
            return self.connection
        except Error as e:
            raise Exception(f"Erro ao obter conexão do pool: {e}")

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
        query_start = time.time()
        
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
                    exec_start = time.time()
                    cur.execute(query, params or ())
                    exec_time = time.time() - exec_start
                    
                    fetch_start = time.time()
                    result = cur.fetchall()
                    fetch_time = time.time() - fetch_start
                    
                    columns = [c[0] for c in cur.description]
                    data = [dict(zip(columns, row)) for row in result]
                    
                    total_time = time.time() - query_start
                    
                    if DB_DEBUG:
                        print(f"[Database] 📊 Query: {exec_time:.4f}s | Fetch: {fetch_time:.4f}s | Total: {total_time:.4f}s | Rows: {len(data)}")
                        # Mostra query resumida (primeiros 100 chars)
                        query_preview = query.strip().replace('\n', ' ')[:100]
                        print(f"[Database] 📝 {query_preview}...")
                    
                    return data
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
        """Retorna a conexão ao pool (não fecha permanentemente)"""
        try:
            if self.connection and self.connection.is_connected():
                # Importante: close() em conexão do pool retorna ela ao pool, não fecha
                self.connection.close()
                if DB_DEBUG:
                    print(f"[Database] 🔄 Conexão retornada ao pool")
        except Error as e:
            if DB_DEBUG:
                print(f"[Database] ⚠️ Erro ao retornar conexão ao pool: {e}")
        finally:
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