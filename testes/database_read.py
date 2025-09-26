# check_seed.py
# -*- coding: utf-8 -*-
from libs.models.database import Database
from textwrap import shorten


def print_usinas(db):
    print("\n=== Usinas (op_usina) ===")
    rows = db.fetch_data("SELECT id, nome, sigla, ativo FROM op_usina ORDER BY id;")
    for r in rows:
        print(f"[{r['id']}] {r['nome']} (sigla={r['sigla']}, ativo={r['ativo']})")


def print_usuarios(db):
    print("\n=== Usuários (op_usuario) ===")
    rows = db.fetch_data("SELECT id, nome, perfil, ativo FROM op_usuario ORDER BY id;")
    for r in rows:
        print(f"[{r['id']}] {r['nome']} (perfil={r['perfil']}, ativo={r['ativo']})")


def print_ocorrencias(db, limit=20):
    print(f"\n=== Ocorrências (op_ocorrencia) - mostrando até {limit} registros ===")
    rows = db.fetch_data(f"""
        SELECT o.id, u.nome AS usina, op.nome AS operador,
               o.tipo, o.categoria, o.unidade,
               o.status, o.severidade, o.created_at, o.descricao
        FROM op_ocorrencia o
        JOIN op_usina u   ON u.id=o.usina_id
        JOIN op_usuario op ON op.id=o.operador_id
        ORDER BY o.created_at
        LIMIT {limit};
    """)
    for r in rows:
        desc = shorten(r['descricao'], width=80, placeholder="...")
        print(f"[{r['id']}] Usina={r['usina']}, Operador={r['operador']}, "
              f"Tipo={r['tipo']}, Categoria={r['categoria']}, "
              f"Status={r['status']}, Severidade={r['severidade']}, "
              f"Data={r['created_at']:%Y-%m-%d %H:%M} \n     Desc: {desc}")


def run_check():
    db = Database()
    try:
        db.connect()
        print_usinas(db)
        print_usuarios(db)
        print_ocorrencias(db, limit=20)  # mostra só 20 primeiros
    finally:
        db.close()


if __name__ == "__main__":
    run_check()
