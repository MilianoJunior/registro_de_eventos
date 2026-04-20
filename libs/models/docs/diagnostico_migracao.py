"""
Diagnóstico de migração Railway → GCloud
Compara tabelas, contagens e datas entre os dois bancos.
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime

CONFIG = {
    "railway": {
        "user": "root",
        "password": "cgG3hDhhc4GcbhF5d2FBf422C-BHhe35",
        "host": "viaduct.proxy.rlwy.net",
        "database": "railway",
        "port": 29893,
        "raise_on_warnings": False,
    },
    "gcloud": {
        "user": "junior",
        "password": "Jun654123@",
        "host": "100.72.202.107",
        "database": "cog",
        "port": 3306,
        "raise_on_warnings": False,
    },
}


def conectar(nome):
    try:
        conn = mysql.connector.connect(**CONFIG[nome])
        print(f"[OK] Conectado ao {nome}")
        return conn
    except Error as err:
        print(f"[ERRO] {nome}: {err}")
        return None


def listar_tabelas(conn):
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tabelas = [row[0] for row in cur.fetchall()]
    cur.close()
    return tabelas


def contar_registros(conn, tabela):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(*) FROM `{tabela}`")
        count = cur.fetchone()[0]
    except Error:
        count = -1
    cur.close()
    return count


def datas_extremas(conn, tabela):
    """Retorna (min_date, max_date) procurando colunas de data comuns."""
    cur = conn.cursor()
    cur.execute(f"SHOW COLUMNS FROM `{tabela}`")
    colunas = [row[0] for row in cur.fetchall()]
    cur.close()

    # Procurar colunas de data em ordem de prioridade
    candidatas = ["created_at", "timestamp", "data_referencia", "data_ocorrencia", "updated_at", "data"]
    col_data = None
    for c in candidatas:
        if c in colunas:
            col_data = c
            break

    if not col_data:
        return None, None, None

    cur = conn.cursor()
    try:
        cur.execute(f"SELECT MIN(`{col_data}`), MAX(`{col_data}`) FROM `{tabela}`")
        row = cur.fetchone()
        return col_data, row[0], row[1]
    except Error:
        return col_data, None, None
    finally:
        cur.close()


def main():
    conn_railway = conectar("railway")
    conn_gcloud = conectar("gcloud")

    if not conn_railway and not conn_gcloud:
        print("[ERRO] Nenhum banco acessível.")
        return

    tabelas_railway = listar_tabelas(conn_railway) if conn_railway else []
    tabelas_gcloud = listar_tabelas(conn_gcloud) if conn_gcloud else []

    todas = sorted(set(tabelas_railway) | set(tabelas_gcloud))

    print("\n" + "=" * 120)
    print(f"{'TABELA':<30} {'RAILWAY':>10} {'GCLOUD':>10} {'DIFF':>10} | {'COL DATA':<18} {'MIN RAILWAY':<22} {'MAX RAILWAY':<22} {'MIN GCLOUD':<22} {'MAX GCLOUD':<22}")
    print("=" * 120)

    for tabela in todas:
        in_r = tabela in tabelas_railway
        in_g = tabela in tabelas_gcloud

        count_r = contar_registros(conn_railway, tabela) if in_r else "-"
        count_g = contar_registros(conn_gcloud, tabela) if in_g else "-"

        if isinstance(count_r, int) and isinstance(count_g, int):
            diff = count_r - count_g
        else:
            diff = "-"

        # Datas
        col_r, min_r, max_r = datas_extremas(conn_railway, tabela) if in_r else (None, None, None)
        col_g, min_g, max_g = datas_extremas(conn_gcloud, tabela) if in_g else (None, None, None)
        col_data = col_r or col_g or "-"

        def fmt(v):
            if v is None:
                return "-"
            if isinstance(v, datetime):
                return v.strftime("%Y-%m-%d %H:%M:%S")
            return str(v)

        status = ""
        if not in_r:
            status = " [SOMENTE GCLOUD]"
        elif not in_g:
            status = " [SOMENTE RAILWAY]"

        print(f"{tabela:<30} {str(count_r):>10} {str(count_g):>10} {str(diff):>10} | {str(col_data):<18} {fmt(min_r):<22} {fmt(max_r):<22} {fmt(min_g):<22} {fmt(max_g):<22}{status}")

    print("=" * 120)
    print(f"\nTotal de tabelas Railway: {len(tabelas_railway)}")
    print(f"Total de tabelas GCloud:  {len(tabelas_gcloud)}")
    print(f"Somente Railway:          {len(set(tabelas_railway) - set(tabelas_gcloud))}")
    print(f"Somente GCloud:           {len(set(tabelas_gcloud) - set(tabelas_railway))}")
    print(f"Em ambos:                 {len(set(tabelas_railway) & set(tabelas_gcloud))}")

    if conn_railway:
        conn_railway.close()
    if conn_gcloud:
        conn_gcloud.close()


if __name__ == "__main__":
    main()
