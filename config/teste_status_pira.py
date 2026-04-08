# -------------------------------------------------------------------
# ARQUIVO TEMPORÁRIO — Teste de leitura dos status das UGs da PCH PIRA
# Registradores baseados em UG-01.py (BIT/BOOLEAN, offset 0)
# IPs baseados em config/usinas_dispositivos.json
#
# Executar: python config/teste_status_pira.py
# -------------------------------------------------------------------

import json
import requests

API_URL    = "http://100.93.197.110:8010"
PORTA      = 502
TIMEOUT_MB = 5
TIMEOUT_HTTP = 20

STATUS_LABEL_ORDER = [
    "US (sincronizado)",
    "UMD (marcha desexcitada)",
    "UPS (pronta para sincronização)",
    "UPGM (pronta para giro mecânico)",
    "UP (parada)",
]

# Registradores extraídos de UG-01.py (UG1_Status_*)
# Assumindo mesmo mapa de registros em cada CLP por ser programa idêntico
STATUS_REGISTERS = {
    "UP (parada)":                        [17099, "BOOLEAN", {"offset": 0}],
    "UPGM (pronta para giro mecânico)":   [17104, "BOOLEAN", {"offset": 0}],
    "UPS (pronta para sincronização)":    [17114, "BOOLEAN", {"offset": 0}],
    "US (sincronizado)":                  [17118, "BOOLEAN", {"offset": 0}],
    "UMD (marcha desexcitada)":           [17109, "BOOLEAN", {"offset": 0}],  # UMVD no CLP
}

# IPs das UGs conforme usinas_dispositivos.json
UGS = {
    "UG-01": "10.200.20.11",
    "UG-02": "10.200.20.21",
    "UG-03": "10.200.20.31",
    "UG-04": "10.200.20.41",
    "UG-05": "10.200.20.51",
}


def _montar_registers(status_regs: dict) -> dict:
    return {nome: [end, tipo, opts] for nome, (end, tipo, opts) in status_regs.items()}


def _ler_ug(nome_ug: str, ip: str) -> dict:
    payload = {
        "conexao": {"ip": ip, "port": PORTA, "timeout": TIMEOUT_MB},
        "registers": _montar_registers(STATUS_REGISTERS),
    }
    try:
        r = requests.post(f"{API_URL}/readCLP/leituras", json=payload, timeout=TIMEOUT_HTTP)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"status": "error", "data": None, "message": str(e)}


def main():
    print(f"\n{'='*65}")
    print(f"  PCH PIRA — Teste de leitura de STATUS das UGs")
    print(f"  API: {API_URL}")
    print(f"{'='*65}")

    for nome_ug, ip in UGS.items():
        print(f"\n  [{nome_ug}] IP: {ip}")
        resultado = _ler_ug(nome_ug, ip)

        if resultado.get("status") != "success":
            print(f"    ERRO: {resultado.get('message', 'sem resposta')}")
            continue

        dados = resultado.get("data") or {}
        if not dados:
            print("    Sem dados retornados.")
            continue

        print(f"    Registradores lidos ({len(dados)}):")
        for nome in STATUS_LABEL_ORDER:
            if nome in dados:
                val = dados[nome]
                end = STATUS_REGISTERS.get(nome, [None])[0]
                print(f"    {'[X]' if val else '[ ]'} {nome} (reg {end}) = {val}")
            else:
                print(f"    [?] {nome} — não retornado")

        print(f"\n    JSON bruto:")
        print(json.dumps(dados, ensure_ascii=False, indent=6))


if __name__ == "__main__":
    main()
