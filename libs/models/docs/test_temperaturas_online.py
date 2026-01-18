# -------------------------------------------------------------------
# FLUXO DO MODULO
# 1. conectar_banco → abre conexao MySQL
# 2. testar_temperaturas_online → consulta op_paradas no banco online
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# CONFIGURACOES, CONSTANTES E MAPAS
# -------------------------------------------------------------------

import mysql.connector
from mysql.connector import Error

CONFIG_ONLINE = {
    "user": "junior",
    "password": "Jun654123@",
    "host": "100.72.202.107",
    "database": "cog",
    "port": 3306,
    "raise_on_warnings": False,
}


def conectar_banco(cfg):
    try:
        return mysql.connector.connect(**cfg)
    except Error as err:
        print(f"[ERRO] conectar_banco: {err}")
        return None


def testar_temperaturas_online():
    conn = conectar_banco(CONFIG_ONLINE)
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM op_paradas")
        total = cursor.fetchone() or {}
        print("[OK] op_paradas total:", total.get("total", 0))

        cursor.execute("SELECT timestamp, dados FROM op_paradas ORDER BY id DESC LIMIT 1")
        ultimo = cursor.fetchone() or {}
        print("[OK] ultimo timestamp:", ultimo.get("timestamp"))
        print("[OK] dados (resumo):", "presente" if ultimo.get("dados") else "vazio")
    except Error as err:
        print(f"[ERRO] consulta: {err}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    testar_temperaturas_online()
