import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import time

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- CONFIGURAÇÃO ---
config = {
    'online': {
        'user': os.getenv('MYSQLUSER'),
        'password': os.getenv('MYSQLPASSWORD'),
        'host': os.getenv('MYSQLHOST'),
        'database': os.getenv('MYSQLDATABASE'),
        'port': int(os.getenv('MYSQLPORT', 3306)),
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

def conectar(cfg, nome):
    print(f"Conectando ao banco de dados {nome}...")
    try:
        conn = mysql.connector.connect(**cfg)
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar no banco {nome}: {err}")
        return None

def criar_tabelas(conn_online, conn_offline, tabelas):
    cursor_online = conn_online.cursor()
    cursor_offline = conn_offline.cursor()
    
    print("\n--- Verificando/Criando Tabelas ---")
    
    for nome_tabela in tabelas:
        try:
            print(f"Obtendo schema para: {nome_tabela}")
            cursor_online.execute(f"SHOW CREATE TABLE {nome_tabela}")
            result = cursor_online.fetchone()
            
            if result:
                create_statement = result[1]
                # Adiciona IF NOT EXISTS para evitar erro se já existir
                create_statement = create_statement.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
                
                print(f"Criando tabela {nome_tabela} no offline...")
                cursor_offline.execute(create_statement)
                conn_offline.commit()
            else:
                print(f"Não foi possível obter o schema de {nome_tabela}")
                
        except mysql.connector.Error as err:
            print(f"Erro ao criar/verificar tabela {nome_tabela}: {err}")
            
    cursor_online.close()
    cursor_offline.close()

def copiar_dados():
    conn_online = conectar(config['online'], 'ONLINE')
    conn_offline = conectar(config['offline'], 'OFFLINE')

    if not conn_online or not conn_offline:
        print("Não foi possível estabelecer conexão com ambos os bancos.")
        return

    # 1. Primeiro garante que as tabelas existem
    # Ordem importante para respeitar chaves estrangeiras
    tabelas_projeto = [
        'op_usina',
        'op_usuario',
        'op_ocorrencia',
        'op_paradas',
        # 'clientes', # Removido pois deu erro na origem
    ]
    
    criar_tabelas(conn_online, conn_offline, tabelas_projeto)

    cursor_online = conn_online.cursor()
    cursor_offline = conn_offline.cursor()

    inicio = time.time()
    print(f"\n--- Iniciando cópia de dados ---")

    for nome_tabela in tabelas_projeto:
        print("=" * 60)
        print(f" TABELA: {nome_tabela.upper()}")
        print("=" * 60)

        try:
            # Ler do online
            cursor_online.execute(f"SELECT * FROM {nome_tabela}")
            colunas = [desc[0] for desc in cursor_online.description]
            registros = cursor_online.fetchall()

            if not registros:
                print(f" (Tabela {nome_tabela} vazia no online)")
            else:
                print(f" Lendo {len(registros)} registros do online...")
                
                # Preparar insert no offline
                cols_str = ", ".join(colunas)
                placeholders = ", ".join(["%s"] * len(colunas))
                # Usando INSERT IGNORE para não duplicar se já existir (pela PK)
                sql_insert = f"INSERT IGNORE INTO {nome_tabela} ({cols_str}) VALUES ({placeholders})"
                
                # Executa em lotes para evitar problemas de memória com tabelas grandes
                batch_size = 1000
                for i in range(0, len(registros), batch_size):
                    batch = registros[i:i + batch_size]
                    cursor_offline.executemany(sql_insert, batch)
                    conn_offline.commit()
                    print(f"  Processados {min(i + batch_size, len(registros))} de {len(registros)} registros...")
                
                print(f" Cópia concluída para {nome_tabela}.")

        except mysql.connector.Error as err:
            print(f"Erro ao processar dados da tabela {nome_tabela}: {err}")
    
    fim = time.time()
    print("\n" + "=" * 60)
    print(f"Tempo total de execução: {fim - inicio:.2f} segundos")
    
    # Fechar conexões
    if cursor_online: cursor_online.close()
    if conn_online: conn_online.close()
    if cursor_offline: cursor_offline.close()
    if conn_offline: conn_offline.close()
    print("Conexões encerradas.")

if __name__ == "__main__":
    copiar_dados()