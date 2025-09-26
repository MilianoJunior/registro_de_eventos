from libs.models.read import OpUsina, OpUsuario, OpOcorrencia
from datetime import datetime, timedelta
import time

# run_reads.py
# -*- coding: utf-8 -*-
"""
Teste manual e simples dos métodos de leitura, usando o banco REAL.
- Sem pytest
- Sem dados fakes
- Só prints e tempos de execução

Requisitos:
- libs/models/database.py (sua classe Database que lê do .env)
- libs/models/read.py (Read, OpUsina, OpUsuario, OpOcorrencia)
"""

from datetime import datetime
import time
import math
from typing import Any, Dict, Iterable, Optional

# Ajuste se seus modelos estiverem em outro caminho:
from libs.models.read import OpUsina, OpUsuario, OpOcorrencia


# ---------------------- utilitários de impressão ----------------------
def hr(title: Optional[str] = None):
    print("\n" + "=" * 90)
    if title:
        print(title)
        print("-" * 90)

def ptime(label: str, t0: float, t1: float):
    dt = t1 - t0
    print(f"⏱ {label}: {dt:.4f} s")

def show_rows(rows: Iterable[Dict[str, Any]], limit: int = 10, truncate: int = 120):
    """
    Imprime dicionários de forma compacta. Trunca campos longos (ex.: descricao).
    """
    count = 0
    for r in rows:
        if count >= limit:
            print(f"... ({limit} de {count} mostrados)")
            break
        # formata uma linha curta
        line_parts = []
        for k, v in r.items():
            s = str(v)
            if truncate and len(s) > truncate:
                s = s[:truncate].rstrip() + "..."
            line_parts.append(f"{k}={s}")
        print(" - " + " | ".join(line_parts))
        count += 1

def show_rows_pretty(rows: Iterable[Dict[str, Any]], limit: int = 10, truncate_fields: Optional[Dict[str, int]] = None):
    """
    Versão levemente mais 'inteligente': trunca só certos campos (ex.: descricao).
    """
    if truncate_fields is None:
        truncate_fields = {"descricao": 120, "playbook": 80, "template_texto": 80}
    shown = 0
    for r in rows:
        if shown >= limit:
            print(f"... (mostrando {limit}, existem mais {len(rows) - limit})")
            break
        # cabeça
        head = []
        for k in ("id", "usina_id", "operador_id", "tipo", "categoria", "unidade", "status", "severidade", "created_at"):
            if k in r:
                head.append(f"{k}={r[k]}")
        if head:
            print("• " + " | ".join(str(x) for x in head))
        # cauda (campos longos)
        for k in ("descricao", "observacao", "playbook", "template_texto", "tags"):
            if k in r and r[k]:
                s = str(r[k])
                tlen = truncate_fields.get(k, None)
                if tlen and len(s) > tlen:
                    s = s[:tlen].rstrip() + "..."
                print(f"    {k}: {s}")
        shown += 1


# ---------------------- cenários de leitura ----------------------
def test_usina():
    hr("USINAS (op_usina)")
    model = OpUsina()

    t0 = time.time()
    all_rows = model.get_all()
    t1 = time.time()
    print(f"Total usinas: {len(all_rows)}")
    show_rows(all_rows, limit=20, truncate=0)
    ptime("get_all", t0, t1)

    # by_id
    if all_rows:
        any_id = all_rows[0]["id"]
        t0 = time.time()
        row = model.get_by_id(any_id)
        t1 = time.time()
        print(f"\nget_by_id({any_id}): {row}")
        ptime("get_by_id", t0, t1)

    # where
    t0 = time.time()
    ativos = model.where({"ativo": 1}, order_by="nome")
    t1 = time.time()
    print(f"\nAtivos: {len(ativos)}")
    show_rows(ativos, limit=20, truncate=0)
    ptime("where ativo=1", t0, t1)

    # count
    t0 = time.time()
    total_ativos = model.count({"ativo": 1})
    t1 = time.time()
    print(f"\nCount ativos: {total_ativos}")
    ptime("count", t0, t1)


def test_usuario():
    hr("USUÁRIOS (op_usuario)")
    model = OpUsuario()

    t0 = time.time()
    ops = model.where({"perfil": "operador", "ativo": 1}, order_by="nome")
    t1 = time.time()
    print(f"Operadores ativos: {len(ops)}")
    show_rows(ops, limit=30, truncate=0)
    ptime("where perfil=operador AND ativo=1", t0, t1)

    # first LIKE
    t0 = time.time()
    um_rr = model.first({"nome": ("like", "%r%")}, order_by="nome")
    t1 = time.time()
    print(f"\nfirst nome LIKE '%r%': {um_rr}")
    ptime("first LIKE", t0, t1)

    # ids_only
    t0 = time.time()
    ids = model.ids_only({"ativo": 1}, limit=50)
    t1 = time.time()
    print(f"\nids_only ativos (<=50): {ids}")
    ptime("ids_only", t0, t1)


def test_ocorrencia():
    hr("OCORRÊNCIAS (op_ocorrencia)")
    model = OpOcorrencia()

    # últimos 20 (ordenado por created_at DESC por padrão)
    t0 = time.time()
    ultimas = model.get_all(limit=20)
    t1 = time.time()
    print(f"Últimas {len(ultimas)} ocorrências:")
    show_rows_pretty(ultimas, limit=20)
    ptime("get_all(limit=20)", t0, t1)

    # por id
    if ultimas:
        any_id = ultimas[0]["id"]
        t0 = time.time()
        row = model.get_by_id(any_id)
        t1 = time.time()
        print(f"\nget_by_id({any_id}):")
        show_rows_pretty([row], limit=1)
        ptime("get_by_id", t0, t1)

    # filtro combinado
    t0 = time.time()
    filtro = model.where({
        "status": "resolvida",
        "severidade": ("in", ["alta", "crítica"]),
        "unidade": ("like", "CGH-PICADAS%"),
    }, limit=20, order_by="created_at", desc=True)
    t1 = time.time()
    print(f"\nFiltro resolvida & severidade in (alta, crítica) & unidade LIKE 'CGH-PICADAS%': {len(filtro)}")
    show_rows_pretty(filtro, limit=20)
    ptime("where combinado", t0, t1)

    # intervalo de datas (por created_at)
    inicio = datetime(2025, 6, 24)
    fim = datetime(2025, 7, 10, 23, 59, 59)
    t0 = time.time()
    intervalo = model.get_between("created_at", start=inicio, end=fim, limit=50, order_by="created_at", desc=False)
    t1 = time.time()
    print(f"\nIntervalo {inicio} a {fim}: {len(intervalo)} registros")
    show_rows_pretty(intervalo, limit=20)
    ptime("get_between(created_at)", t0, t1)

    # count por status
    for st in ("aberta", "em_andamento", "resolvida", "cancelada"):
        t0 = time.time()
        n = model.count({"status": st})
        t1 = time.time()
        print(f"count status={st}: {n}")
        ptime(f"count status={st}", t0, t1)

    # ids_only em_andamento
    t0 = time.time()
    ids = model.ids_only({"status": "em_andamento"}, limit=50)
    t1 = time.time()
    print(f"\nids_only(status='em_andamento', limit=50): {ids}")
    ptime("ids_only em_andamento", t0, t1)


def test_reads():
    hr("TESTE SIMPLES DE LEITURAS (BANCO REAL)")
    try:
        test_usina()
        test_usuario()
        test_ocorrencia()
    except Exception as e:
        print("\n❌ Erro durante os testes manuais:", e)
    finally:
        print("\n✅ Fim dos testes manuais")
