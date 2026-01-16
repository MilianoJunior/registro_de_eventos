# -------------------------------------------------------------------
# FLUXO DO MODULO
# 1. conectar_banco → abre conexao MySQL
# 2. obter_schema_tabela → captura CREATE TABLE da origem
# 3. criar_tabela_online → cria tabela no online com IF NOT EXISTS
# 4. copiar_dados_tabela → copia dados offline → online
# 5. migrar_rats_offline_para_online → orquestra a migracao
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# CONFIGURACOES, CONSTANTES E MAPAS
# -------------------------------------------------------------------

import mysql.connector
from mysql.connector import Error

CONFIG_BANCO = {
    "online": {
        "user": "junior",
        "password": "Jun654123@",
        "host": "100.72.202.107",
        "database": "cog",
        "port": 3306,
        "raise_on_warnings": False,
    },
    "offline": {
        "user": "jrmfilho23",
        "password": "jr88869892",
        "host": "localhost",
        "database": "engesep",
        "port": 3306,
        "raise_on_warnings": False,
    },
}

TABELAS_RATS = [
    # "produtos",
    # "rats",
    # "rat_servicos",
    # "rat_materiais",
    # "rat_fotos",
    # "clientes",
    "op_usuario",
]


def conectar_banco(cfg, nome):
    try:
        return mysql.connector.connect(**cfg)
        
    except Error as err:
        print(f"[ERRO] conectar_banco {nome}: {err}")
        return None


def obter_schema_tabela(cursor_origem, nome_tabela):
    cursor_origem.execute(f"SHOW CREATE TABLE {nome_tabela}")
    row = cursor_origem.fetchone()
    return row[1] if row else ""


def criar_tabela_online(cursor_online, nome_tabela, schema_create):
    if not schema_create:
        print(f"[AVISO] Schema vazio: {nome_tabela}")
        return
    schema_create = schema_create.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1)
    cursor_online.execute(schema_create)


def copiar_dados_tabela(cursor_offline, cursor_online, nome_tabela):
    cursor_offline.execute(f"SELECT * FROM {nome_tabela}")
    colunas = [desc[0] for desc in cursor_offline.description]
    registros = cursor_offline.fetchall()
    if not registros:
        print(f"[INFO] Tabela vazia: {nome_tabela}")
        return
    cols_str = ", ".join(colunas)
    placeholders = ", ".join(["%s"] * len(colunas))
    sql_insert = f"INSERT IGNORE INTO {nome_tabela} ({cols_str}) VALUES ({placeholders})"
    cursor_online.executemany(sql_insert, registros)
    print(f"[OK] {nome_tabela}: {len(registros)} registros")


def migrar_rats_offline_para_online():
    conn_offline = conectar_banco(CONFIG_BANCO["offline"], "OFFLINE")
    conn_online = conectar_banco(CONFIG_BANCO["online"], "ONLINE")
    if not conn_offline or not conn_online:
        print("[ERRO] Conexao offline/online indisponivel")
        return
    cursor_offline = conn_offline.cursor()
    cursor_online = conn_online.cursor()
    try:
        cursor_online.execute("SET FOREIGN_KEY_CHECKS=0")
        for tabela in TABELAS_RATS:
            # Para a tabela 'usuarios', deletar antes de criar novamente
            if tabela == "op_usuario":
                print(f"[INFO] Dropando tabela existente: {tabela}")
                cursor_online.execute(f"DROP TABLE IF EXISTS {tabela}")

            schema_create = obter_schema_tabela(cursor_offline, tabela)
            criar_tabela_online(cursor_online, tabela, schema_create)
            copiar_dados_tabela(cursor_offline, cursor_online, tabela)
            conn_online.commit()
    except Error as err:
        print(f"[ERRO] migrar_rats_offline_para_online: {err}")
        conn_online.rollback()
    finally:
        cursor_online.execute("SET FOREIGN_KEY_CHECKS=1")
        cursor_offline.close()
        cursor_online.close()
        conn_offline.close()
        conn_online.close()


if __name__ == "__main__":
    migrar_rats_offline_para_online()
