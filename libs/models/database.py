# libs/models/database.py
import mysql.connector
from mysql.connector import Error, pooling
import os
import time
from threading import Lock
from dotenv import load_dotenv

load_dotenv()

DB_DEBUG = False  # Mude para True para debug verboso

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

class Database(object):  # Removido Singleton
    def __init__(self):
        self.pool = get_connection_pool()
        self.connection = None  # Conexão exclusiva desta instância

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

    def close(self):
        """Retorna a conexão ao pool (não fecha permanentemente)"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close() # Devolve ao pool
                if DB_DEBUG:
                    print(f"[Database] 🔄 Conexão retornada ao pool")
        except Error as e:
            if DB_DEBUG:
                print(f"[Database] ⚠️ Erro ao retornar conexão ao pool: {e}")
        finally:
            self.connection = None

    # ---- Execução de Queries ----

    def execute_query(self, query, params=None):
        """Executa query de modificação (INSERT, UPDATE, DELETE)."""
        cur = None
        try:
            self.connect()
            cur = self.connection.cursor()
            cur.execute(query, params or ())
            self.connection.commit()
            return cur # Retorna cursor para pegar lastrowid se necessário
        except Error as e:
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            raise Exception(f"Erro ao executar query: {e}")
        finally:
            if cur:
                try:
                    cur.close()
                except:
                    pass
            # Em non-singleton, fechamos/devolvemos a conexão imediatamente após o uso atomicamente
            self.close()

    def execute_many(self, queries):
        """Executa múltiplas queries em transação."""
        cur = None
        try:
            self.connect()
            cur = self.connection.cursor()
            for q in queries:
                if q and q.strip():
                    cur.execute(q)
            self.connection.commit()
        except Error as e:
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            raise Exception(f"Erro ao executar batch: {e}")
        finally:
            if cur:
                try:
                    cur.close()
                except:
                    pass
            self.close()

    def fetch_data(self, query, params=None):
        """Busca dados (SELECT)."""
        cur = None
        try:
            self.connect()
            # Dictionary cursor para retornar dicts
            # Nota: mysql.connector puro não tem dict cursor nativo fácil no pool sem configuração extra,
            # então fazemos conversão manual para garantir compatibilidade.
            cur = self.connection.cursor()
            
            query_start = time.time()
            cur.execute(query, params or ())
            
            result = cur.fetchall()
            
            if cur.description:
                columns = [c[0] for c in cur.description]
                data = [dict(zip(columns, row)) for row in result]
            else:
                data = []

            if DB_DEBUG:
                 total_time = time.time() - query_start
                 print(f"[Database] 📊 Query executada em {total_time:.4f}s | Rows: {len(data)}")

            return data
        except Error as e:
            raise Exception(f"Erro ao buscar dados: {e}")
        finally:
            if cur:
                try:
                    cur.close()
                except:
                    pass
            self.close()

    # ---- context manager ----
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except:
            pass
