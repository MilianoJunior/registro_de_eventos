# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _montar_payload_leitura → monta JSON (conexão + registers) para a API
# 2. _ler_um_ip → POST /readCLP/leituras e normaliza resposta
# 3. ler_mapeamento_em_tempo_real → percorre MAPEAMENTO_UG01 por IP
# 4. _meta_endereco_tipo → extrai endereço e tipo (REAL/WORD/…) do mapeamento
# 5. _imprimir_snapshot → exibe leituras; opcionalmente JSON bruto retornado pela API
# 6. main → loop periódico até Ctrl+C
# -------------------------------------------------------------------

import json
import time
from datetime import datetime

import requests

from new_leitura import MAPEAMENTO_UG01

# --- CONFIGURAÇÕES (mesmo padrão do main.py — API atrás do Tailscale na Pira) ---
API_URL = "http://100.93.197.110:8010"
PORTA_MODBUS = 502
TIMEOUT_MODBUS = 5
TIMEOUT_HTTP = 20
INTERVALO_SEGUNDOS = 2.0
# True = imprime o dict completo da API por IP (status, data, message, extras) para depuração
EXIBIR_JSON_RESPOSTA_API = True
# True = imprime também o JSON enviado no POST (conexao + registers)
EXIBIR_JSON_PAYLOAD_ENVIADO = False


def _montar_payload_leitura(ip: str, registers: dict) -> dict:
    return {
        "conexao": {
            "ip": ip,
            "port": PORTA_MODBUS,
            "timeout": TIMEOUT_MODBUS,
        },
        "registers": registers,
    }


def _ler_um_ip(
    ip: str,
    registers: dict,
    verbose: bool,
    guardar_payload: bool = False,
) -> dict:
    payload = _montar_payload_leitura(ip, registers)
    try:
        r = requests.post(
            f"{API_URL}/readCLP/leituras",
            json=payload,
            timeout=TIMEOUT_HTTP,
        )
        r.raise_for_status()
        body = r.json()
    except requests.RequestException as e:
        if verbose:
            print(f"  [{ip}] ERRO HTTP: {e}")
        return {"status": "error", "data": None, "message": str(e)}

    status = body.get("status", "?")
    if status != "success" and verbose:
        print(f"  [{ip}] API: {body.get('message', body)}")
    if guardar_payload:
        body = {**body, "_payload_enviado": payload}
    return body


def ler_mapeamento_em_tempo_real(
    mapeamento: dict | None = None,
    verbose: bool = True,
    anexar_payload_na_resposta: bool | None = None,
) -> dict:
    """
    Lê todos os IPs do mapeamento (CLP, QCC, relé, etc.) na mesma rodada.
    Retorno: { ip: { "status", "data", "message" } }
    """
    anexar = (
        EXIBIR_JSON_PAYLOAD_ENVIADO
        if anexar_payload_na_resposta is None
        else anexar_payload_na_resposta
    )
    alvo = mapeamento if mapeamento is not None else MAPEAMENTO_UG01
    saida = {}
    for ip, registers in alvo.items():
        if not registers:
            continue
        saida[ip] = _ler_um_ip(
            ip,
            registers,
            verbose=verbose,
            guardar_payload=anexar,
        )
    return saida


def _meta_endereco_tipo(def_registro) -> tuple:
    """
    def_registro: [endereco, tipo_modbus, {opcional}] ex.: [2588, "INPUT_REAL", {...}]
    """
    if not def_registro or not isinstance(def_registro, (list, tuple)) or len(def_registro) < 2:
        return ("?", "?")
    end, tipo = def_registro[0], def_registro[1]
    return (end, tipo if tipo is not None else "?")


def _imprimir_snapshot(
    leituras: dict,
    mapeamento: dict | None = None,
) -> None:
    alvo_map = mapeamento if mapeamento is not None else MAPEAMENTO_UG01
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*72}\n  PCH PIRA — snapshot {ts}\n{'='*72}")
    for ip, resultado in leituras.items():
        if EXIBIR_JSON_RESPOSTA_API:
            exibir = dict(resultado)
            if not EXIBIR_JSON_PAYLOAD_ENVIADO:
                exibir.pop("_payload_enviado", None)
            print(f"\n  <<< JSON retorno API [{ip}] >>>")
            print(
                json.dumps(exibir, ensure_ascii=False, indent=2, default=str),
            )
        st = resultado.get("status", "?")
        dados = resultado.get("data") or {}
        if st != "success" or not dados:
            msg = resultado.get("message", "sem dados")
            print(f"\n  [{ip}] status={st} — {msg}")
            continue
        regs_ip = alvo_map.get(ip, {})
        print(f"\n  [{ip}] ({len(dados)} variáveis)")
        cont = 0
        for nome in sorted(dados.keys(), key=str.lower):
            val = dados[nome]
            cont += 1
            end, tipo_mb = _meta_endereco_tipo(regs_ip.get(nome))
            sufixo = f" | end={end} tipo={tipo_mb}"
            if isinstance(val, float):
                print(f" {cont} -  {nome}: {val:.4f}{sufixo}")
            else:
                print(f" {cont} -  {nome}: {val}{sufixo}")


def main() -> None:
    print("Leitura em tempo real — um POST por IP do MAPEAMENTO_UG01")
    print(f"API: {API_URL} | intervalo: {INTERVALO_SEGUNDOS}s (Ctrl+C para sair)")
    try:
        while True:
            leituras = ler_mapeamento_em_tempo_real(verbose=True)
            _imprimir_snapshot(leituras)
            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")


if __name__ == "__main__":
    main()
