# run_edits.py
# -*- coding: utf-8 -*-
"""
Testes manuais dos métodos de edição (UPDATE) usando o banco REAL.
- Sem pytest
- Sem mocks
- Com prints, tempos e REVERT ao final

O script valida:
1) update_by_id em op_usina (flip no campo 'ativo' e revert)
2) update_where em op_ocorrencia (troca 'tags' e revert)
3) set_json_key em op_ocorrencia.metadata (insere chave temporária e remove)

Requisitos:
- libs/models/database.py   (Database com singleton)
- libs/models/utils.py      (com build_where_clause/build_update_sql/etc.)
- libs/models/read.py       (Read/OpUsina/OpOcorrencia)
- libs/models/edit.py       (Edit/OpUsinaEdit/OpOcorrenciaEdit)
"""

import time
from datetime import datetime

from libs.models.database import Database
from libs.models.read import OpUsina, OpOcorrencia
from libs.models.edit import OpUsinaEdit, OpOcorrenciaEdit


# ---------------------- utilitários ----------------------
def hr(title: str = ""):
    print("\n" + "=" * 90)
    if title:
        print(title)
        print("-" * 90)

def ptime(label: str, t0: float, t1: float):
    print(f"⏱ {label}: {t1 - t0:.4f} s")

def preview_usina(urow):
    if not urow:
        print("usina: (vazia)")
        return
    print(f"usina[id={urow['id']}] nome={urow['nome']} sigla={urow.get('sigla')} ativo={urow['ativo']}")

def preview_oc(o):
    if not o:
        print("ocorrencia: (vazia)")
        return
    head = f"oc[id={o['id']}] usina_id={o['usina_id']} operador_id={o['operador_id']} status={o['status']} severidade={o['severidade']}"
    print(head)
    print("   unidade=", o['unidade'])
    if o.get("tags"):
        print("   tags=", o["tags"])
    if o.get("metadata") is not None:
        print("   metadata=", o["metadata"])


# ---------------------- testes ----------------------
def test_update_by_id_usina():
    hr("EDIT #1 - update_by_id em op_usina (flip campo 'ativo' com REVERT)")
    r = OpUsina()
    e = OpUsinaEdit()

    # pega a primeira usina (id menor) só pra testar
    t0 = time.time()
    usinas = r.get_all(limit=1, order_by="id", desc=False)
    t1 = time.time()
    ptime("fetch usina (baseline)", t0, t1)

    if not usinas:
        print("Nenhuma usina encontrada.")
        return

    u0 = usinas[0]
    preview_usina(u0)

    original_ativo = int(u0["ativo"])
    flip_ativo = 0 if original_ativo == 1 else 1

    # aplica update_by_id
    t0 = time.time()
    rows = e.update_by_id(u0["id"], {"ativo": flip_ativo})
    t1 = time.time()
    print(f"update_by_id -> rowcount={rows}")
    ptime("update_by_id", t0, t1)

    # confere
    u1 = r.get_by_id(u0["id"])
    print("Depois do update:")
    preview_usina(u1)

    # REVERT
    t0 = time.time()
    e.update_by_id(u0["id"], {"ativo": original_ativo})
    t1 = time.time()
    ptime("revert update_by_id", t0, t1)

    u2 = r.get_by_id(u0["id"])
    print("Depois do revert:")
    preview_usina(u2)


def test_update_where_op_ocorrencia():
    hr("EDIT #2 - update_where em op_ocorrencia (altera 'tags' com REVERT)")
    r = OpOcorrencia()
    e = OpOcorrenciaEdit()

    # pega a ocorrência mais recente
    t0 = time.time()
    oc_list = r.get_all(limit=1)  # default DESC by created_at
    t1 = time.time()
    ptime("fetch ocorrencia (baseline)", t0, t1)

    if not oc_list:
        print("Nenhuma ocorrência encontrada.")
        return

    oc0 = oc_list[0]
    preview_oc(oc0)

    oc_id = int(oc0["id"])
    original_tags = oc0.get("tags") or ""
    new_tags = "teste-auto" if "teste-auto" not in original_tags else original_tags.replace("teste-auto", "").strip(", ").strip()

    # update_where com condição por id (pode combinar com outros filtros se quiser)
    t0 = time.time()
    rows = e.update_where({"id": oc_id}, {"tags": new_tags})
    t1 = time.time()
    print(f"update_where(tags) -> rowcount={rows}")
    ptime("update_where(tags)", t0, t1)

    oc1 = r.get_by_id(oc_id)
    print("Depois do update(tags):")
    preview_oc(oc1)

    # REVERT
    t0 = time.time()
    e.update_where({"id": oc_id}, {"tags": original_tags})
    t1 = time.time()
    ptime("revert update_where(tags)", t0, t1)

    oc2 = r.get_by_id(oc_id)
    print("Depois do revert(tags):")
    preview_oc(oc2)


def test_set_json_key_op_ocorrencia():
    hr("EDIT #3 - set_json_key em op_ocorrencia.metadata (add/remove chave temporária)")
    r = OpOcorrencia()
    e = OpOcorrenciaEdit()

    # ocorrência mais recente novamente
    oc_list = r.get_all(limit=1)
    if not oc_list:
        print("Nenhuma ocorrência encontrada.")
        return

    oc0 = oc_list[0]
    oc_id = int(oc0["id"])
    key = "tmp_teste"  # chave temporária (alfanumérica/_)

    # 1) set_json_key -> adiciona/atualiza a chave
    t0 = time.time()
    rows = e.set_json_key({"id": oc_id}, "metadata", key, {"ok": True, "ts": datetime.now().isoformat()})
    t1 = time.time()
    print(f"set_json_key -> rowcount={rows}")
    ptime("set_json_key", t0, t1)

    oc1 = r.get_by_id(oc_id)
    print("Depois do set_json_key:")
    preview_oc(oc1)

    # 2) remover chave (usando JSON_REMOVE)
    #    Obs: implementando aqui direto pra não alongar a classe (pode virar util depois).
    db = Database()
    db.connect()
    json_path = f"$.{key}"
    sql = (
        "UPDATE `op_ocorrencia` "
        "SET `metadata` = JSON_REMOVE(`metadata`, %s) "
        "WHERE `id` = %s"
    )
    t0 = time.time()
    cur = db.execute_query(sql, (json_path, oc_id))
    t1 = time.time()
    print(f"JSON_REMOVE -> rowcount={cur.rowcount if cur else 0}")
    ptime("JSON_REMOVE", t0, t1)

    oc2 = r.get_by_id(oc_id)
    print("Depois do remove key:")
    preview_oc(oc2)


def test_edits():
    hr("TESTES MANUAIS: EDIT (UPDATE)")
    try:
        # “pré-aquece” a conexão pra tirar o pico inicial
        Database().connect()

        test_update_by_id_usina()
        test_update_where_op_ocorrencia()
        test_set_json_key_op_ocorrencia()

    except Exception as e:
        print("\n❌ Erro durante os testes de edição:", e)
    finally:
        print("\n✅ Fim dos testes de edição.")


if __name__ == "__main__":
    test_edits()
