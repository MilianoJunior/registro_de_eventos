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
    }
}

inserir_dados = {
    "op_usuario": [
        {
        "nome":"Eduardo",
        "email":"eduardo@engesep.com.br",
        "perfil":"operador",
        "cargo":"Técnico em Eletrônica",
        "assinatura":"assets/assinaturas/eduardo.png",
        "ativo":1
    },
    ],
}

def inserir_dados_online():
    conn_online = conectar_banco(CONFIG_BANCO["online"], "ONLINE")
    if not conn_online:
        print("[ERRO] Conexao online indisponivel")
        return
    cursor_online = conn_online.cursor()
    try:
        cursor_online.execute("SET FOREIGN_KEY_CHECKS=0")
        for tabela in inserir_dados:
            for dados in inserir_dados[tabela]:
                sql_insert = f"INSERT INTO {tabela} ({', '.join(dados.keys())}) VALUES ({', '.join(['%s'] * len(dados))})"
                cursor_online.execute(sql_insert, list(dados.values()))
        conn_online.commit()
    except Error as err:
        print(f"[ERRO] inserir_dados_online: {err}")
        conn_online.rollback()
    finally:
        cursor_online.execute("SET FOREIGN_KEY_CHECKS=1")
        cursor_online.close()
        conn_online.close()


if __name__ == "__main__":
    inserir_dados_online()