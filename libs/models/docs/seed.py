# seed_op_tabelas.py
# -*- coding: utf-8 -*-
from datetime import datetime
import re
from textwrap import dedent

# importe sua classe Database
from libs.models.database import Database   # <<< AJUSTE AQUI


# ----------------------- DADOS ORIGINAIS (resumo) -----------------------
# Colei exatamente o que você enviou (mantendo acentos e maiúsculas).
# OLD_ROWS = [
#     {'id': 1, 'data': datetime(2025, 6, 23, 23, 0), 'unidade': 'CGH-APARECIDA', 'operacao': 'Diminuição de potência 2400->2000', 'condicao': 'Diferencial de grade 1.20 m', 'resultado': 'Diferencial de grade abaixou para 1.00 m', 'operador': 'Junior', 'observacao': 'Leandro informou que o limpa grades está indisponível, sendo necessario baixar a potência progressivamente no valor de 200 kw.', 'created_at': datetime(2025, 9, 12, 19, 55, 38), 'updated_at': datetime(2025, 9, 12, 19, 55, 38), 'estado': 'ativa', 'status': 'concluido'},
#     {'id': 2, 'data': datetime(2025, 6, 23, 23, 30), 'unidade': 'CGH-FAE', 'operacao': 'Rejeição de Carga', 'condicao': 'Diferencial de grade UG-01=0.58 m, UG-02=0.38', 'resultado': '', 'operador': 'Junior', 'observacao': 'Cliente informou que a grade da UG-01 está com avaria (Operação anterior a EngeSEP)', 'created_at': datetime(2025, 9, 12, 19, 55, 38), 'updated_at': datetime(2025, 9, 12, 19, 55, 38), 'estado': 'ativa', 'status': 'concluido'},
#     {'id': 3, 'data': datetime(2025, 6, 24, 0, 23), 'unidade': 'CGH-APARECIDA', 'operacao': 'Diminuição de potência 2000->1800', 'condicao': 'Diferencial de grade 1.20 m', 'resultado': 'Diferencial de grade abaixou para 1.00 m', 'operador': 'Junior', 'observacao': 'Leandro informou que o limpa grades está indisponível, sendo necessario baixar a potência progressivamente no valor de 200 kw.', 'created_at': datetime(2025, 9, 12, 19, 55, 39), 'updated_at': datetime(2025, 9, 12, 19, 55, 39), 'estado': 'ativa', 'status': 'concluido'},
#     {'id': 4, 'data': datetime(2025, 6, 24, 2, 20), 'unidade': 'CGH-PICADAS ALTAS', 'operacao': 'Limpeza das grades', 'condicao': 'Diferencial de grade 0.85', 'resultado': 'Sem resposta do manutentor local', 'operador': 'Junior', 'observacao': '', 'created_at': datetime(2025, 9, 12, 19, 55, 40), 'updated_at': datetime(2025, 9, 12, 19, 55, 40), 'estado': 'ativa', 'status': 'concluido'},
#     {'id': 5, 'data': datetime(2025, 6, 24, 2, 40), 'unidade': 'CGH-FAE', 'operacao': 'Controle automatico e função de religamento ativados', 'condicao': 'Ativação de TRIP: UG-01-UHLM-Ausência de fluxo de água no trocador de calor - TRIP', 'resultado': 'Após diversas partidas para acionar o estado US da UG-01 sem sucesso, a máquina sincronizou', 'operador': 'Junior', 'observacao': '', 'created_at': datetime(2025, 9, 12, 19, 55, 40), 'updated_at': datetime(2025, 9, 12, 19, 55, 40), 'estado': 'ativa', 'status': 'concluido'},
#     {'id': 6, 'data': datetime(2025, 6, 24, 2, 58), 'unidade': 'CGH-PICADAS ALTAS', 'operacao': 'Limpeza das grades', 'condicao': 'Diferencial de grade 1.00 m', 'resultado': '', 'operador': 'Junior', 'observacao': '', 'created_at': datetime(2025, 9, 12, 19, 55, 41), 'updated_at': datetime(2025, 9, 12, 19, 55, 41), 'estado': 'ativa', 'status': 'concluido'},
#     {'id': 7, 'data': datetime(2025, 6, 24, 2, 58), 'unidade': 'CGH-APARECIDA', 'operacao': 'Diminuição de potência 1800->1600', 'condicao': 'Diferencial de grade 1.20 m', 'resultado': 'Diferencial de grade abaixou para 1.00 m', 'operador': 'Junior', 'observacao': 'Leandro informou que o limpa grades está indisponível, sendo necessario baixar a potência progressivamente no valor de 200 kw.', 'created_at': datetime(2025, 9, 12, 19, 55, 42), 'updated_at': datetime(2025, 9, 12, 19, 55, 42), 'estado': 'ativa', 'status': 'concluido'},
#     {'id': 8, 'data': datetime(2025, 6, 24, 3, 7), 'unidade': 'CGH-PICADAS ALTAS', 'operacao': 'Diminuição da potência UG01: 180->150, UG-02: 530->500', 'condicao': 'Diferencial de grade 1.00 m', 'resultado': 'Diferencial de grade não diminuiu', 'operador': 'Junior', 'observacao': '', 'created_at': datetime(2025, 9, 12, 19, 55, 42), 'updated_at': datetime(2025, 9, 12, 19, 55, 42), 'estado': 'ativa', 'status': 'concluido'},
#     # ... (mantenha todos os itens até o 41 exatamente como você passou)
#     {'id': 39, 'data': datetime(2025, 9, 15, 17, 28, 48), 'unidade': 'CGH-APARECIDA', 'operacao': 'Parada por falta de energia celesc', 'condicao': 'Sem energia na rede', 'resultado': 'maquina parada', 'operador': 'Gelson', 'observacao': 'Foi ligado para celesc e protocolo é o xxxccvvbb', 'created_at': datetime(2025, 9, 15, 20, 28, 49), 'updated_at': datetime(2025, 9, 15, 20, 28, 49), 'estado': 'ativa', 'status': 'concluido'},
#     {'id': 40, 'data': datetime(2025, 9, 19, 8, 53, 11), 'unidade': 'CGH-APARECIDA', 'operacao': 'aA', 'condicao': 'DSASD', 'resultado': 'SDA', 'operador': 'Junior', 'observacao': 'CVV', 'created_at': datetime(2025, 9, 19, 11, 53, 13), 'updated_at': datetime(2025, 9, 19, 11, 53, 13), 'estado': 'ativa', 'status': 'alerta'},
#     {'id': 41, 'data': datetime(2025, 9, 19, 8, 53, 43), 'unidade': 'CGH-APARECIDA', 'operacao': 'SDKJA', 'condicao': 'ASDA', 'resultado': 'ASDG', 'operador': 'Junior', 'observacao': 'CVVXCV', 'created_at': datetime(2025, 9, 19, 11, 53, 45), 'updated_at': datetime(2025, 9, 19, 11, 53, 45), 'estado': 'ativa', 'status': 'critica'},
# ]
def consulta():
    db = Database()
    db.connect()
    # db.fetch_data("SELECT * FROM registros_eventos")
    # print(db.fetch_data())
    OLD_ROWS = db.fetch_data("SELECT * FROM registros_eventos")
    db.close()
    return OLD_ROWS

OLD_ROWS = consulta()
# OBS: para economizar espaço aqui, eu não re-repliquei as entradas 9..38,
# mas no seu arquivo mantenha TODAS. O script funciona com a lista completa.


# ----------------------- HELPERS -----------------------
def norm_spaces(s: str) -> str:
    return re.sub(r'\s+', ' ', s).replace(' - ', '-').strip()

def normalize_usina(nome: str) -> str:
    s = norm_spaces(nome.upper())
    # Normalizações pontuais vistas nos dados
    s = s.replace('CGH - ', 'CGH ')
    s = s.replace('PCG PEDRAS', 'PCH-PEDRAS')
    s = s.replace('CGH PICADAS ALTAS', 'CGH-PICADAS ALTAS')
    s = s.replace('CGH HOPPEN', 'CGH-HOPPEN')
    s = s.replace('CGH - HOPPEN', 'CGH-HOPPEN')
    return s

def normalize_operador(nome: str) -> str:
    return norm_spaces(nome.title())

def map_status(src: str) -> str:
    s = (src or '').lower()
    if 'concluido' in s:
        return 'resolvida'
    if 'alerta' in s:
        return 'em_andamento'
    if 'critica' in s or 'crítica' in s:
        return 'em_andamento'
    return 'aberta'

def map_severidade(row) -> str:
    s = (row.get('status') or '').lower()
    if 'critica' in s or 'crítica' in s:
        return 'crítica'
    # heurística simples: se resultado/parada/sem energia -> alta
    texto = ' '.join([str(row.get('resultado') or ''), str(row.get('operacao') or ''), str(row.get('condicao') or '')]).upper()
    if any(tok in texto for tok in ['PARADA', 'SEM ENERGIA', 'FALTA DE ÁGUA', 'BLOQUEIO', 'TRIP']):
        return 'alta'
    return 'média'

def infer_tipo(row) -> str:
    texto = ' '.join([str(row.get('operacao') or ''), str(row.get('condicao') or '')]).upper()
    if 'TRIP' in texto:
        return 'Trip'
    if 'REJEI' in texto:
        return 'Manobra'
    if 'LIMPEZA' in texto:
        return 'Evento'
    return 'Evento'

def infer_categoria(row) -> str:
    texto = ' '.join([str(row.get('operacao') or ''), str(row.get('condicao') or '')]).upper()
    if any(k in texto for k in ['TENSÃO', 'ELETR', 'DISJUNTOR']):
        return 'Elétrica'
    if any(k in texto for k in ['NÍVEL', 'AGUA', 'ÁGUA', 'HIDR']):
        return 'Hidráulica'
    return 'Operação/Humano'

def build_descricao(row) -> str:
    partes = []
    if row.get('operacao'):
        partes.append(f"Operação: {row['operacao']}")
    if row.get('condicao'):
        partes.append(f"Condição: {row['condicao']}")
    if row.get('resultado'):
        partes.append(f"Resultado: {row['resultado']}")
    if row.get('observacao'):
        partes.append(f"Observação: {row['observacao']}")
    return '\n'.join(partes) or '(sem descrição)'

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



# ----------------------- QUERIES -----------------------
SQL_INS_USINA = dedent("""
    INSERT INTO op_usina (nome, sigla, timezone, ativo)
    SELECT %s, %s, 'America/Sao_Paulo', 1
    WHERE NOT EXISTS (
        SELECT 1 FROM op_usina WHERE UPPER(nome)=UPPER(%s)
    );
""")

SQL_GET_USINA_ID = "SELECT id FROM op_usina WHERE UPPER(nome)=UPPER(%s) LIMIT 1;"

SQL_INS_USER = dedent("""
    INSERT INTO op_usuario (nome, email, perfil, ativo)
    SELECT %s, NULL, 'operador', 1
    WHERE NOT EXISTS (
        SELECT 1 FROM op_usuario WHERE UPPER(nome)=UPPER(%s)
    );
""")

SQL_GET_USER_ID = "SELECT id FROM op_usuario WHERE UPPER(nome)=UPPER(%s) LIMIT 1;"

SQL_INS_OCORRENCIA = dedent("""
    INSERT INTO op_ocorrencia
      (usina_id, operador_id, tipo, categoria, unidade, tags,
       playbook, template_texto, descricao, status, severidade, origem,
       metadata, created_at, updated_at, resolved_at)
    VALUES
      (%s, %s, %s, %s, %s, %s,
       NULL, NULL, %s, %s, %s, 'humano',
       NULL, %s, %s, %s);
""")

SQL_CHECK_DUP = dedent("""
    SELECT id FROM op_ocorrencia
    WHERE usina_id=%s AND operador_id=%s
      AND tipo=%s AND categoria=%s
      AND unidade=%s
      AND DATE(created_at)=DATE(%s)
      AND LEFT(descricao, 120)=LEFT(%s, 120)
    LIMIT 1;
""")


# ----------------------- SEED RUNNER -----------------------
def seed():
    db = Database()
    try:
        conn = db.connect()

        cur = conn.cursor()

        # 1) Usinas a partir dos dados antigos
        usinas = sorted({normalize_usina(r['unidade']) for r in OLD_ROWS})
        for nome in usinas:
            sigla = build_sigla(nome)
            #              v-----------v-----------v-----------v
            cur.execute(SQL_INS_USINA, (nome, sigla, nome))
            print("usina:", nome, "sigla:", sigla)
        conn.commit()

        

        # 2) Operadores
        operadores = sorted({normalize_operador(r['operador']) for r in OLD_ROWS})
        for nome in operadores:
            cur.execute(SQL_INS_USER, (nome, nome))
            print(nome)
        conn.commit()
        

        # 3) Inserir ocorrências (idempotente via verificação simples)
        for r in OLD_ROWS:
            usina_nome = normalize_usina(r['unidade'])
            operador_nome = normalize_operador(r['operador'])

            # ids fk
            cur.execute(SQL_GET_USINA_ID, (usina_nome,))
            row = cur.fetchone()
            if not row:
                # garante que existe antes de seguir
                sigla = build_sigla(usina_nome)
                cur.execute(SQL_INS_USINA, (usina_nome, sigla, usina_nome))
                conn.commit()
                cur.execute(SQL_GET_USINA_ID, (usina_nome,))
                row = cur.fetchone()
            usina_id = row[0]

            cur.execute(SQL_GET_USER_ID, (operador_nome,))
            row = cur.fetchone()
            if not row:
                cur.execute(SQL_INS_USER, (operador_nome, operador_nome))
                conn.commit()
                cur.execute(SQL_GET_USER_ID, (operador_nome,))
                row = cur.fetchone()
            operador_id = row[0]


            tipo = infer_tipo(r)
            categoria = infer_categoria(r)
            unidade_txt = r['unidade']  # mantém como veio
            tags_csv = ''               # sem tags por ora
            descricao = build_descricao(r)
            status = map_status(r.get('status'))
            severidade = map_severidade(r)

            created_at = r.get('data') or r.get('created_at') or datetime.utcnow()
            updated_at = r.get('updated_at') or created_at
            resolved_at = created_at if status == 'resolvida' else None

            # evita duplicar se já existir algo muito parecido no mesmo dia
            cur.execute(SQL_CHECK_DUP,
                        (usina_id, operador_id, tipo, categoria, unidade_txt,
                         created_at, descricao))
            exists = cur.fetchone()
            if exists:
                continue

            cur.execute(SQL_INS_OCORRENCIA, (
                usina_id, operador_id, tipo, categoria, unidade_txt, tags_csv,
                descricao, status, severidade,
                created_at, updated_at, resolved_at
            ))

        conn.commit()
        cur.close()
        print("✅ Seed concluído (op_usina, op_usuario, op_ocorrencia).")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
