import mysql.connector
from mysql.connector import Error

conexao = {
    'user': 'junior',
    'password': 'Jun654123@',
    'host': '100.72.202.107',
    'database': 'cog',
    'port': 3306,
    'raise_on_warnings': False
}


def listar_tabelas(cursor):
    cursor.execute("SHOW TABLES")
    return [row[0] for row in cursor.fetchall()]


def ler_tabela(cursor, nome_tabela, limite=5):
    cursor.execute(f"SELECT * FROM `{nome_tabela}` LIMIT {limite}")
    colunas = [desc[0] for desc in cursor.description]
    registros = cursor.fetchall()
    return colunas, registros


def main():
    try:
        conn = mysql.connector.connect(**conexao)
    except Error as err:
        print(f"[ERRO] Falha ao conectar: {err}")
        return

    cursor = conn.cursor()
    try:
        tabelas = listar_tabelas(cursor)
        if not tabelas:
            print("[INFO] Nenhuma tabela encontrada.")
            return

        for tabela in tabelas:
            print("=" * 60)
            print(f"TABELA: {tabela}")
            colunas, registros = ler_tabela(cursor, tabela, limite=5)
            if not registros:
                print("  (vazia)")
                continue
            print("  Colunas:", colunas)
            for i, row in enumerate(registros, start=1):
                print(f"  {i}) {row}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()