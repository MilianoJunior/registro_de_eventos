# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _hosts_ips_pch_pira → (área, papel, ip) a partir de ips_pch_pira; ignora MASK/GATEWAY
# 2. tcp_probe / http_probe / mqtt_probe / opcua_probe / modbus_probe → sondas por protocolo
# 3. executar_probe_no_host → varre portas comuns e testa protocolos em um IP
# 4. main → executa executar_probe_no_host em todos os hosts do mapa
# -------------------------------------------------------------------

ips_pch_pira = {
    "GERAL": {
        "SUPERVISORIO": "10.200.20.5",
        "MASK": "255.255.255.0",
        "GATEWAY": "10.200.20.1"
    },
    "UG01": {
        "CLP": "10.200.20.11",
        "QCC-UG01": "10.200.20.14",
        "IHM": "10.200.20.12",
        "RELE": "10.200.20.13",
    },
    "UG02": {
        "CLP": "10.200.20.21",
        "IHM": "10.200.20.22",
        "RELE": "10.200.20.23",
        "QCC-UG02": "10.200.20.24"
    },
    "UG03": {
        "CLP": "10.200.20.31",
        "IHM": "10.200.20.32",
        "RELE": "10.200.20.33",
        "QCC-UG03": "10.200.20.34"
    },
    "UG04": {
        "CLP": "10.200.20.41",
        "IHM": "10.200.20.42",
        "RELE": "10.200.20.43",
        "QCC-UG04": "10.200.20.44"
    },
    "MINI CENTRAL": {
        "CLP": "10.200.20.51",
        "IHM": "10.200.20.52",
        "RELE": "10.200.20.53"
    },
    "PSA": {
        "CLP": "10.200.20.61",
        "IHM": "10.200.20.62",
        "RELE 787": "10.200.20.63",
        "RELE 751": "10.200.20.64",
        "GMG": "10.200.20.65"
    }
}

import asyncio
import logging
import socket
import ssl
from dataclasses import dataclass
from typing import List, Tuple

import requests

# Dependências opcionais:
# pip install paho-mqtt asyncua pymodbus requests
try:
    import paho.mqtt.client as mqtt
except Exception:
    mqtt = None

try:
    from asyncua import Client as OPCUAClient
except Exception:
    OPCUAClient = None

try:
    from pymodbus.client import AsyncModbusTcpClient
except Exception:
    AsyncModbusTcpClient = None


TIMEOUT = 3.0

_CHAVES_IGNORADAS_MAPA = frozenset({"MASK", "GATEWAY"})

COMMON_PORTS = [
    80,    # HTTP
    443,   # HTTPS
    4840,  # OPC UA
    1883,  # MQTT
    8883,  # MQTT TLS
    502,   # Modbus TCP
    8080,  # HTTP alternativo
    8081,
    8000,
    8001,
    9000,
]


@dataclass
class ProbeResult:
    service: str
    host: str
    port: int
    status: str
    detail: str


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def _hosts_ips_pch_pira(arvore: dict) -> List[Tuple[str, str, str]]:
    """Lista (área, equipamento, ip) para cada host; mascara/gateway ficam de fora."""
    saida: List[Tuple[str, str, str]] = []
    for area, bloco in arvore.items():
        if not isinstance(bloco, dict):
            continue
        for papel, host in bloco.items():
            if papel in _CHAVES_IGNORADAS_MAPA:
                continue
            if not isinstance(host, str):
                continue
            partes = host.split(".")
            if len(partes) != 4 or not all(p.isdigit() for p in partes):
                continue
            if not all(0 <= int(p) <= 255 for p in partes):
                continue
            saida.append((str(area), str(papel), host))
    return saida


def tcp_probe(host: str, port: int, timeout: float = 3.0) -> Tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "porta aberta"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def http_probe(host: str, port: int, https: bool = False, timeout: float = 3.0) -> ProbeResult:
    scheme = "https" if https else "http"
    url = f"{scheme}://{host}:{port}/"
    try:
        r = requests.get(url, timeout=timeout, verify=False)
        server = r.headers.get("Server", "desconhecido")
        return ProbeResult(
            service=scheme.upper(),
            host=host,
            port=port,
            status="OK",
            detail=f"status={r.status_code}, server={server}, len={len(r.text)}"
        )
    except Exception as e:
        return ProbeResult(
            service=scheme.upper(),
            host=host,
            port=port,
            status="FAIL",
            detail=f"{type(e).__name__}: {e}"
        )


async def mqtt_probe(host: str, port: int, timeout: float = 4.0) -> ProbeResult:
    if mqtt is None:
        return ProbeResult("MQTT", host, port, "SKIP", "paho-mqtt não instalado")

    loop = asyncio.get_running_loop()
    connected = asyncio.Event()
    result = {"rc": None, "msg": ""}

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.enable_logger()

    def on_connect(client_, userdata, flags, rc):
        result["rc"] = rc
        result["msg"] = f"on_connect rc={rc}"
        connected.set()

    def on_disconnect(client_, userdata, rc):
        logging.info("MQTT disconnect rc=%s", rc)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(host, port, keepalive=10)
        client.loop_start()

        try:
            await asyncio.wait_for(connected.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return ProbeResult("MQTT", host, port, "FAIL", "timeout aguardando CONNACK")

        if result["rc"] == 0:
            return ProbeResult("MQTT", host, port, "OK", "broker respondeu ao CONNECT")
        return ProbeResult("MQTT", host, port, "FAIL", result["msg"])

    except Exception as e:
        return ProbeResult("MQTT", host, port, "FAIL", f"{type(e).__name__}: {e}")
    finally:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass


async def opcua_probe(host: str, port: int, timeout: float = 5.0) -> ProbeResult:
    if OPCUAClient is None:
        return ProbeResult("OPC_UA", host, port, "SKIP", "asyncua não instalado")

    url = f"opc.tcp://{host}:{port}"
    client = OPCUAClient(url=url, timeout=timeout)

    try:
        await client.connect()
        endpoints = await client.connect_and_get_server_endpoints()
        names = [f"{ep.EndpointUrl}" for ep in endpoints[:5]]
        return ProbeResult(
            "OPC_UA",
            host,
            port,
            "OK",
            f"endpoints={len(endpoints)} primeiros={names}"
        )
    except Exception as e:
        return ProbeResult("OPC_UA", host, port, "FAIL", f"{type(e).__name__}: {e}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass


async def modbus_probe(host: str, port: int, timeout: float = 4.0) -> ProbeResult:
    if AsyncModbusTcpClient is None:
        return ProbeResult("MODBUS", host, port, "SKIP", "pymodbus não instalado")

    client = AsyncModbusTcpClient(host, port=port, timeout=timeout, retries=1)
    try:
        ok = await client.connect()
        connected_state = getattr(client, "connected", None)

        if not ok or not connected_state:
            return ProbeResult(
                "MODBUS",
                host,
                port,
                "FAIL",
                f"connect={ok}, connected={connected_state}"
            )

        # leitura mínima e inocente
        rr = await client.read_holding_registers(address=0, count=2, slave=1)
        if rr.isError():
            return ProbeResult("MODBUS", host, port, "PARTIAL", f"conectou, mas leitura retornou erro: {rr}")

        return ProbeResult("MODBUS", host, port, "OK", f"regs={rr.registers}")

    except Exception as e:
        return ProbeResult("MODBUS", host, port, "FAIL", f"{type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except Exception:
            pass


async def executar_probe_no_host(host: str) -> None:
    open_ports: List[int] = []
    for port in COMMON_PORTS:
        ok, detail = tcp_probe(host, port, TIMEOUT)
        status = "ABERTA" if ok else "fechada"
        print(f"TCP {host}:{port:<5} -> {status} | {detail}")
        if ok:
            open_ports.append(port)

    print("\n=== TESTES DE PROTOCOLO ===\n")

    results: List[ProbeResult] = []

    if 80 in open_ports:
        results.append(http_probe(host, 80, https=False, timeout=TIMEOUT))
    if 443 in open_ports:
        results.append(http_probe(host, 443, https=True, timeout=TIMEOUT))
    for p in [8080, 8081, 8000, 8001, 9000]:
        if p in open_ports:
            results.append(http_probe(host, p, https=False, timeout=TIMEOUT))

    if 1883 in open_ports:
        results.append(await mqtt_probe(host, 1883, timeout=TIMEOUT))
    if 8883 in open_ports:
        results.append(await mqtt_probe(host, 8883, timeout=TIMEOUT))

    if 4840 in open_ports:
        results.append(await opcua_probe(host, 4840, timeout=TIMEOUT))

    if 502 in open_ports:
        results.append(await modbus_probe(host, 502, timeout=TIMEOUT))

    if not results:
        print("Nenhum protocolo candidato respondeu nas portas testadas.")
        print("\n=== CONCLUSÃO RÁPIDA ===")
        print("- Nada confirmado ainda. Pode haver porta não padrão, autenticação, ou protocolo proprietário.")
        return

    for r in results:
        print(f"{r.service:<8} {r.host}:{r.port:<5} -> {r.status:<7} | {r.detail}")

    print("\n=== CONCLUSÃO RÁPIDA ===")
    ok_services = [r for r in results if r.status == "OK"]
    if ok_services:
        for r in ok_services:
            print(f"- {r.service} parece utilizável em {r.host}:{r.port}")
    else:
        print("- Nada confirmado ainda. Pode haver porta não padrão, autenticação, ou protocolo proprietário.")


async def main():
    requests.packages.urllib3.disable_warnings()  # type: ignore
    alvos = _hosts_ips_pch_pira(ips_pch_pira)
    if not alvos:
        print("ips_pch_pira não retornou nenhum host (verifique o mapa).")
        return

    print(f"\n>>> {len(alvos)} host(s) no mapa ips_pch_pira — probe sequencial\n")

    for area, papel, ip in alvos:
        print("\n" + "=" * 72)
        print(f"=== PROBE  {area}  |  {papel}  |  {ip}")
        print("=" * 72)
        await executar_probe_no_host(ip)


if __name__ == "__main__":
    asyncio.run(main())

