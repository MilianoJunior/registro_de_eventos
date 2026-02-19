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


def _carregar_incluidos():
    """Carrega o CSV e retorna (incluidos, a_conferir, excluidos, tabela_original)."""
    import pandas as pd
    import os

    projeto_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    csv_path = os.path.join(projeto_root, 'assets', 'clientes', 'clientes.csv')
    tabela = pd.read_csv(csv_path, sep=';', encoding='utf-8')

    nomes_comuns = [
        'APARECIDA', 'FAE', 'HOPPEN', 'PICADAS', 'PIRA', 'PEDRAS', 'USINA', 'PCH', 'CGH',
        'HIDREL', 'ENERGIA', 'GERAÇÃO', 'PRODUÇÃO DE ENERGIA', 'CENTRAL AURORA',
        'SIEMENS INFRAESTRUTURA', 'WEG', 'HIDROELETRICA', 'ENGESEP', 'ENERGETICA',
        'MTS SISTEMAS', 'A.CABINE MATERIAIS', 'TURBINAS HIDRAULICAS', 'HIDROGERADORES',
        'QUANTA GERACAO', 'PRIME GROUP SOLAR', 'ESB ENGENHARIA LTDA',
        'SAO SEBASTIAO EMPREENDIMENTOS', 'ENGEPOWER', 'ENERTRAFO', 'INDUSUL',
        'HYDROWHEEL', 'HACKER', 'REDE ELÉTRICA',
    ]
    nomes_nao_inserir = [
        'HOTEL', 'COMERCIO', 'RESTAURANTE', 'CHURRASCARIA', 'POUSADA', 'AGENCIA', 'HOTELARIA',
        'TURISMO', 'PARK', 'POSTO', 'COMBUSTIVEIS', 'TRANSPORTES', 'FERRAMENTAS', 'SHOPPING',
        'DISTRIBUIDORA', 'PREFEITURA', 'DESPACHANTE', 'COMERCIAL', 'COMERCIALIZADORA',
        'COMERCIALIZACAO', 'SITES', 'HOSPEDAGEM', 'HOSPITAL', 'HOSPITAIS', 'ELETRONICOS',
        'AUTOMOVEIS', 'AUTOMOTIVO', 'AUTOMOTIVA', 'COMIDA', 'MINISTERIO', 'MEDICINA',
        'LABORATORIO', 'DECORACAO', 'CLINICA', 'SECRETARIA', 'ELETROPLASTICOS', 'FUTEBOL',
        'ENCOMENDAS', 'METALURGIA', 'METALURGICA', 'GRAFICA', 'TRANSPORTADORES',
        'TRANSPORTADORA', 'PNEUS', 'MECANICA', 'RESTAURANT', 'BONES', 'BORRACHA', 'TELAS',
        'PAPEL', 'VEICULOS', 'TRANSPS', 'COZINHA', 'LANCHES', 'PARAFUSOS', 'PIZZARIA',
        'LOCADORA', 'LOCACAO', 'INVIOLAVEL', 'SEGURADORA', 'SEGURANCA', 'VIGILANCIA',
        'ESTOFADOS', 'MÓVEIS', 'EXPRESSO',
    ]

    def _deve_ignorar(nome: str) -> bool:
        nome_upper = str(nome).upper()
        return any(t in nome_upper for t in nomes_nao_inserir)

    def _deve_incluir(nome: str) -> bool:
        nome_upper = str(nome).upper()
        return any(t in nome_upper for t in nomes_comuns)

    mascara_excluir  = tabela['Nome'].apply(_deve_ignorar) | tabela['Fantasia'].apply(_deve_ignorar)
    tabela_filtrada  = tabela[~mascara_excluir]
    tabela_excluidos = tabela[mascara_excluir]

    mascara_incluir   = tabela_filtrada['Nome'].apply(_deve_incluir) | tabela_filtrada['Fantasia'].apply(_deve_incluir)
    tabela_incluidos  = tabela_filtrada[mascara_incluir]
    tabela_a_conferir = tabela_filtrada[~mascara_incluir]

    return tabela_incluidos, tabela_a_conferir, tabela_excluidos, tabela


def insert_clientes():
    '''
    ============================================================
    TABELA: CLIENTES
    ============================================================
    COLUNAS: id | nome_razao | cnpj | cidade | obras
    ------------------------------------------------------------
    1
    6 | IPIRA ENERGIA SA | 26.986.376/0001-00 | IPIRA - SC | PCH-PIRA
    ------------------------------------------------------------
    2
    5 | EUCLIDES MACIEL ENERGETICA AS | 08.812.700/0001-92 | ÁGUA DOCE - SC | PCH-PEDRAS
    ------------------------------------------------------------
    3
    4 | PICADAS ALTAS ENERGIA SPE LTDA | 41.234.054/0001-07 | LAGEADO GRANDE - SC | CGH-PICADAS-ALTAS
    ------------------------------------------------------------
    4
    3 | CAVEIRAS ENERGIA LTDA | 38.352.880/0001-38 | LAGES - SC | CGH-HOPPEN
    ------------------------------------------------------------
    5
    2 | FAÉ ENERGÉTICA LTDA | 32.927.636/0001-70 | CAMPOS NOVOS - SC | CGH-FAE
    ------------------------------------------------------------
    6
    1 | APARECIDA ENERGIA LTDA | 23.607.291/0001-86 | ENTRE RIOS - SC | CGH-APARECIDA
    ------------------------------------------------------------
    Total de registros: 6
    ------------------------------------------------------------
    '''
    tabela_incluidos, tabela_a_conferir, tabela_excluidos, tabela = _carregar_incluidos()

    def _imprimir_grupo(titulo: str, df) -> None:
        print(f'\n{"="*60}')
        print(f'  {titulo}: {len(df)} registros')
        print(f'{"="*60}')
        df_exibir = df[['Nome', 'Fantasia']].reset_index(drop=True)
        df_exibir.index += 1
        print(df_exibir.to_string())

    _imprimir_grupo('INCLUÍDOS (nomes_comuns)', tabela_incluidos)
    _imprimir_grupo('A CONFERIR',               tabela_a_conferir)
    _imprimir_grupo('EXCLUÍDOS',                tabela_excluidos)

    # tabela de observações — independente dos filtros, direto da origem
    col_obs = 'Observação'
    tabela_obs = tabela[tabela[col_obs].notna() & (tabela[col_obs].str.strip() != '')][['Nome', 'Fantasia', col_obs]].reset_index(drop=True)
    tabela_obs.index += 1

    print(f'\n{"="*60}')
    print(f'  COM OBSERVAÇÃO: {len(tabela_obs)} registros')
    print(f'{"="*60}')
    print(tabela_obs.to_string())

    nomes_set = set(tabela_incluidos['Nome'].str.strip())
    obs_ja    = tabela_obs[tabela_obs['Nome'].str.strip().isin(nomes_set)]
    obs_nao   = tabela_obs[~tabela_obs['Nome'].str.strip().isin(nomes_set)]

    print(f'\n  >> JÁ INCLUÍDOS ({len(obs_ja)}):')
    for nome in obs_ja['Nome']:
        print(f'     ✔ {nome}')

    print(f'\n  >> FORA DOS INCLUÍDOS ({len(obs_nao)}):')
    for nome in obs_nao['Nome']:
        print(f'     ✘ {nome}')


def insert_dados_clientes():
    """Insere apenas os INCLUÍDOS na tabela clientes do banco online.

    Mapeamento CSV → banco:
        nome_razao = Nome
        cnpj       = CPF/CNPJ
        cidade     = Cidade + ' - ' + Estado
        obras      = Fantasia  (NaN → usa Nome como fallback)

    Campos obrigatórios (nome_razao, cnpj, cidade): NaN → loga erro e pula.
    """
    import pandas as pd

    tabela_incluidos, _, _, _ = _carregar_incluidos()

    sql = "INSERT INTO clientes (nome_razao, cnpj, cidade, obras) VALUES (%s, %s, %s, %s)"

    conexao  = mysql.connector.connect(**config)
    cursor   = conexao.cursor()
    inseridos, pulados = 0, 0

    try:
        for _, row in tabela_incluidos.iterrows():
            nome_razao = str(row['Nome']).strip()
            cnpj       = row['CPF/CNPJ']
            cidade_val = row['Cidade']
            estado_val = row['Estado']
            fantasia   = row['Fantasia']

            # Fantasia NaN → fallback para Nome
            obras = nome_razao if pd.isna(fantasia) else str(fantasia).strip()

            # campos obrigatórios com NaN → pula e loga
            campos_faltando = {
                k: v for k, v in {'cnpj': cnpj, 'cidade': cidade_val, 'estado': estado_val}.items()
                if pd.isna(v)
            }
            if campos_faltando:
                print(f'  ✘ Pulado [{nome_razao}] — campos ausentes: {list(campos_faltando.keys())}')
                print(f'     Dados: cnpj={cnpj} | cidade={cidade_val} | estado={estado_val} | obras={obras}')
                pulados += 1
                continue

            cidade = f"{str(cidade_val).strip()} - {str(estado_val).strip()}"
            cnpj   = str(cnpj).strip()

            try:
                cursor.execute(sql, (nome_razao, cnpj, cidade, obras))
                inseridos += 1
            except mysql.connector.Error as err:
                print(f'  ✘ Erro DB em [{nome_razao}]: {err}')
                pulados += 1

        conexao.commit()
        print(f'\n✔ Inserção concluída: {inseridos} inseridos | {pulados} pulados')
    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    # consultar_banco()
    # insert_clientes()
    insert_dados_clientes()
    # 248, 731, 117
    # 298, 682, 116
    # 319, 661, 116
    # 361, 619, 116