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

def conectar_banco(cfg, nome):
    try:
        return mysql.connector.connect(**cfg)
    except Error as err:
        print(f"[ERRO] conectar_banco {nome}: {err}")
        return None

import re

def build_sigla(nome: str) -> str:
    """
    Tenta extrair uma sigla curta (3-6 chars) do nome da usina.
    Exemplos:
      'CGH-APARECIDA'      -> 'APAR'
      'PCH-PEDRAS'         -> 'PED'
      'CGH PICADAS ALTAS'  -> 'PICALT'
      'CGH HOPPEN'         -> 'HOP'
    """
    n = (nome or "").upper()
    # pega a parte depois de 'CGH'/'PCH' ou o último token
    partes = re.split(r'[-\s]+', n)
    # remove prefixos comuns
    partes = [p for p in partes if p not in ('CGH', 'PCH', 'PCG', 'CGH,')]
    base = ''.join(partes) if len(partes) > 1 else (partes[-1] if partes else n)
    # monta uma sigla curta
    if len(partes) >= 2:
        # junta 3 primeiras do primeiro e 3 do segundo (ex.: PIC + ALT)
        s = partes[0][:3] + (partes[1][:3] if len(partes) > 1 else '')
    else:
        s = base[:4]
    return re.sub(r'[^A-Z0-9]', '', s) or 'USI'

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
    "op_usina": [
        {
        "nome":"PCH PIRA",
        "sigla":build_sigla("PCH PIRA"),
        "timezone":"America/Sao_Paulo",
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