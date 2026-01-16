import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import time

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- CONFIGURAÇÃO ---
# MYSQLHOST=127.0.0.1
# MYSQLPORT=3306
# MYSQLUSER=junior
# MYSQLPASSWORD=Jun654123@
# MYSQLDATABASE=cog

config = {
    'online': {
        'user': 'junior',
        'password': 'Jun654123@',
        'host': '100.72.202.107',
        'database': 'cog',
        'port': 3306,
        'raise_on_warnings': False
    },
    'offline': {
        'user': 'jrmfilho23',
        'password': 'jr88869892',
        'host': 'localhost',
        'database': 'engesep',
        'port': 3306,
        'raise_on_warnings': False
    }
}
config = config['online']

def formatar_valor(valor):
    """Função auxiliar para tratar valores None ou objetos de data na impressão"""
    if valor is None:
        return "NULL"
    return str(valor)

def consultar_banco():
    conexao = None
    cursor = None
    
    try:
        print("Conectando ao banco de dados...")
        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()

        # 1. Descobrir quais tabelas existem no banco
        cursor.execute("SHOW TABLES")
        tabelas = cursor.fetchall()

        if not tabelas:
            print("Nenhuma tabela encontrada no banco de dados.")
            return

        print(f"Foram encontradas {len(tabelas)} tabelas.\n")

        # 2. Percorrer cada tabela e mostrar os dados
        for tabela in tabelas:
            nome_tabela = tabela[0]
            
            print("=" * 60)
            print(f" TABELA: {nome_tabela.upper()}")
            print("=" * 60)

            try:
                # Seleciona tudo da tabela atual
                cursor.execute(f"SELECT * FROM {nome_tabela} ORDER BY id DESC LIMIT 10")

                
                # Pega os nomes das colunas
                colunas = [desc[0] for desc in cursor.description]
                registros = cursor.fetchall()

                # Imprime Cabeçalho das Colunas
                header = " | ".join(colunas)
                print(f"COLUNAS: {header}")
                print("-" * 60)
                cont = 0

                # Imprime Linhas
                if not registros:
                    print(" (Tabela vazia)")
                else:
                    for row in registros:
                        cont += 1
                        print(f"{cont}")
                        # Converte cada item para string para evitar erro de print
                        linha_formatada = " | ".join([formatar_valor(item) for item in row])
                        print(f" {linha_formatada}")
                        print("-" * 60)
                print(f"Total de registros: {cont}")
                print("-" * 60)
                print("\n") # Pula linha entre tabelas

            except mysql.connector.Error as err:
                print(f"Erro ao ler tabela {nome_tabela}: {err}")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro: Usuário ou senha inválidos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Erro: Banco de dados não existe.")
        else:
            print(f"Erro de conexão: {err}")
    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()
            print("Conexão encerrada.")

if __name__ == "__main__":
    consultar_banco()