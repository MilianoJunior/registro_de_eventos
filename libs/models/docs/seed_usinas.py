# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _usina_existe   → verifica se a usina já existe no banco
# 2. _inserir_usina  → insere a usina na tabela op_usina
# 3. seed_pch_pira   → orquestra inserção da PCH-PIRA
# -------------------------------------------------------------------
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
sys.path.insert(0, ROOT_DIR)

from libs.models.database import Database

# -------------------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------------------
NOVA_USINA = {
    'nome': 'PCH-PIRA',
    'sigla': 'PIRA',
    'timezone': 'America/Sao_Paulo',
    'ativo': 1,
}

# -------------------------------------------------------------------
# FUNÇÕES
# -------------------------------------------------------------------
def _usina_existe(cur, nome):
    """Retorna True se a usina já existe (comparação case-insensitive)."""
    cur.execute(
        "SELECT id FROM op_usina WHERE UPPER(nome) = UPPER(%s) LIMIT 1",
        (nome,)
    )
    return cur.fetchone() is not None


def _inserir_usina(cur, dados):
    """Insere uma usina na tabela op_usina."""
    cur.execute(
        "INSERT INTO op_usina (nome, sigla, timezone, ativo) VALUES (%s, %s, %s, %s)",
        (dados['nome'], dados['sigla'], dados['timezone'], dados['ativo'])
    )


def seed_pch_pira():
    """Insere a PCH-PIRA no banco local (idempotente)."""
    db = Database()
    try:
        conn = db.connect()
        cur = conn.cursor()

        if _usina_existe(cur, NOVA_USINA['nome']):
            print(f"ℹ️  Usina '{NOVA_USINA['nome']}' já existe, nada a fazer.")
        else:
            _inserir_usina(cur, NOVA_USINA)
            conn.commit()
            print(f"✔ Usina '{NOVA_USINA['nome']}' (sigla={NOVA_USINA['sigla']}) inserida com sucesso.")

        cur.close()
    finally:
        db.close()


if __name__ == '__main__':
    seed_pch_pira()
