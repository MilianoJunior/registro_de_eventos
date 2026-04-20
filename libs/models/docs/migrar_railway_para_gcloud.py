"""
Script para migrar tabelas do Railway para o GCloud.
Copia estrutura (CREATE TABLE) e dados (INSERT em batches) usando threads.
"""
import mysql.connector
from mysql.connector import Error
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys

# ===================== CONFIGURAÇÕES =====================
RAILWAY = {
    "host": "viaduct.proxy.rlwy.net",
    "port": 29893,
    "user": "root",
    "password": "cgG3hDhhc4GcbhF5d2FBf422C-BHhe35",
    "database": "railway",
}

GCLOUD = {
    "host": "100.72.202.107",
    "port": 3306,
    "user": "junior",
    "password": "Jun654123@",
    "database": "cog",
}

BATCH_SIZE = 10000
MAX_THREADS = 6

# Tabelas que existem no Railway mas NÃO no GCloud
TABELAS = [
    "Tokens",
    "Usinas",
    "cgh_alexandre_rossi",
    "cgh_becker",
    "cgh_frozza",
    "cgh_granada",
    "cgh_hoppen_ug01",
    "cgh_hoppen_ug02",
    "cgh_maria_luz",
    "cgh_parisoto",
    "cgh_ponte_caida",
    "cgh_ponte_serrada",
    "cgh_sebastiao_paz_almeida",
    "disponibilidade",
    "eventos",
    "geracaoAcumulada",
    "jasp_test",
    "mc01Analogicas",
    "mc01Regulador",
    "mc01SATEC",
    "mc01SEL700G",
    "producao_historica",
    "psaSATEC",
    "registros_eventos",
    "sumarioAlarmes",
    "sync_state",
    "ug01Analogicas",
    "ug01Regulador",
    "ug01SEL700G",
    "ug02Analogicas",
    "ug02Regulador",
    "ug02SEL700G",
    "ug03Analogicas",
    "ug03Regulador",
    "ug03SEL700G",
    "ug04Analogicas",
    "ug04Regulador",
    "ug04SEL700G",
    "usuarios",
]


def get_connection(config):
    return mysql.connector.connect(**config)


def get_create_table_sql(tabela):
    """Busca o CREATE TABLE do Railway."""
    conn = get_connection(RAILWAY)
    cursor = conn.cursor()
    cursor.execute(f"SHOW CREATE TABLE `{tabela}`")
    row = cursor.fetchone()
    create_sql = row[1]
    cursor.close()
    conn.close()
    return create_sql


def get_row_count(tabela):
    """Conta registros na tabela do Railway."""
    conn = get_connection(RAILWAY)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM `{tabela}`")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def migrar_tabela(tabela):
    """Migra uma tabela completa: cria estrutura + copia dados em batches."""
    inicio = time.time()
    try:
        # 1. Criar tabela no GCloud
        create_sql = get_create_table_sql(tabela)
        conn_gcloud = get_connection(GCLOUD)
        cursor_gcloud = conn_gcloud.cursor()
        cursor_gcloud.execute(f"DROP TABLE IF EXISTS `{tabela}`")
        cursor_gcloud.execute(create_sql)
        conn_gcloud.commit()
        cursor_gcloud.close()
        conn_gcloud.close()

        # 2. Contar registros
        total = get_row_count(tabela)
        if total == 0:
            elapsed = time.time() - inicio
            print(f"  ✓ {tabela}: tabela vazia criada ({elapsed:.1f}s)")
            return tabela, True, 0, time.time() - inicio

        # 3. Copiar dados em batches
        conn_railway = get_connection(RAILWAY)
        cursor_railway = conn_railway.cursor()

        conn_gcloud = get_connection(GCLOUD)
        cursor_gcloud = conn_gcloud.cursor()

        # Pegar nomes das colunas
        cursor_railway.execute(f"SELECT * FROM `{tabela}` LIMIT 1")
        colunas = [desc[0] for desc in cursor_railway.description]
        cursor_railway.fetchall()  # limpar buffer

        placeholders = ", ".join(["%s"] * len(colunas))
        colunas_escaped = ", ".join([f"`{c}`" for c in colunas])
        insert_sql = f"INSERT INTO `{tabela}` ({colunas_escaped}) VALUES ({placeholders})"

        offset = 0
        inseridos = 0
        while offset < total:
            cursor_railway.execute(
                f"SELECT * FROM `{tabela}` LIMIT {BATCH_SIZE} OFFSET {offset}"
            )
            rows = cursor_railway.fetchall()
            if not rows:
                break

            cursor_gcloud.executemany(insert_sql, rows)
            conn_gcloud.commit()
            inseridos += len(rows)
            offset += BATCH_SIZE

            pct = min(100, inseridos * 100 // total)
            print(f"  [{tabela}] {inseridos}/{total} ({pct}%)")

        cursor_railway.close()
        conn_railway.close()
        cursor_gcloud.close()
        conn_gcloud.close()

        elapsed = time.time() - inicio
        print(f"  ✓ {tabela}: {inseridos} registros migrados ({elapsed:.1f}s)")
        return tabela, True, inseridos, elapsed

    except Error as e:
        elapsed = time.time() - inicio
        print(f"  ✗ {tabela}: ERRO - {e} ({elapsed:.1f}s)")
        return tabela, False, 0, elapsed


def main():
    print("=" * 60)
    print("MIGRAÇÃO RAILWAY → GCLOUD")
    print(f"Tabelas: {len(TABELAS)} | Threads: {MAX_THREADS} | Batch: {BATCH_SIZE}")
    print("=" * 60)

    inicio_total = time.time()
    resultados = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(migrar_tabela, t): t for t in TABELAS}
        for future in as_completed(futures):
            resultado = future.result()
            resultados.append(resultado)

    # Resumo
    elapsed_total = time.time() - inicio_total
    sucesso = [r for r in resultados if r[1]]
    falha = [r for r in resultados if not r[1]]
    total_registros = sum(r[2] for r in resultados)

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Sucesso: {len(sucesso)}/{len(TABELAS)} tabelas")
    print(f"Registros migrados: {total_registros:,}")
    print(f"Tempo total: {elapsed_total:.1f}s ({elapsed_total/60:.1f} min)")

    if falha:
        print(f"\nTabelas com ERRO ({len(falha)}):")
        for r in falha:
            print(f"  - {r[0]}")

    return 0 if not falha else 1


if __name__ == "__main__":
    sys.exit(main())
