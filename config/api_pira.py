import asyncio
import struct
from turtle import down
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
import os
import math
import time
from contextlib import asynccontextmanager
import logging
from typing import Any, Callable, Iterable
from collections import deque

# -----------------------------------------------------------
# 1 -Configuração via variáveis de ambiente (ou valores padrão)
# -----------------------------------------------------------
IP_API = os.environ.get("API_HOST", "0.0.0.0")
PORT_API = os.environ.get("API_PORT", "8010")
ALLOWED_ORIGINS = ["*"]
IDLE_TIMEOUT_SECONDS = float(os.environ.get("MODBUS_IDLE_TIMEOUT", "120"))
CLEANUP_INTERVAL_SECONDS = float(os.environ.get("MODBUS_CLEANUP_INTERVAL", "35"))
# -----------------------------------------------------------
# 1.1 - Configuração de Logging (Rotate: 5MB x 3 arquivos)
# -----------------------------------------------------------
from logging.handlers import RotatingFileHandler

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.log")

# Handler de Rotação (Max 5MB, mantém 3 arquivos anteriores)
file_handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes=5 * 1024 * 1024, # 5 MB
    backupCount=3,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        file_handler,
        logging.StreamHandler()
    ]
)

# -----------------------------------------------------------
# 2 - Funções auxiliares
# -----------------------------------------------------------
def word_list_to_long(words: Iterable[int], big_endian: bool = True) -> int:
    words = list(words)
    if not big_endian:
        words = list(reversed(words))
    return (words[0] << 16) + words[1]


def decode_ieee(val_int: int) -> float:
    return struct.unpack("f", struct.pack("I", val_int))[0]


def float_to_word_list(value: float, big_endian: bool = True) -> list[int]:
    packed = struct.pack("f", value)
    int_val = struct.unpack("I", packed)[0]
    high = (int_val >> 16) & 0xFFFF
    low = int_val & 0xFFFF
    return [high, low] if big_endian else [low, high]


def _swap_words(words: list[int]) -> list[int]:
    return list(reversed(words))


def _swap_bytes(word: int) -> int:
    return ((word & 0xFF) << 8) | ((word >> 8) & 0xFF)


def _swap_bytes_each(words: list[int]) -> list[int]:
    return [_swap_bytes(word) for word in words]


def _apply_read_conversion(words: list[int], converter: str | None) -> list[int]:
    if converter is None:
        converter = "default"

    if converter == "default":
        return _swap_words(words)
    if converter == "endianness":
        return words
    if converter == "word_order":
        return _swap_words(words)
    if converter == "byte_order":
        return _swap_words(_swap_bytes_each(words))
    if converter == "swap":
        return _swap_bytes_each(words)

    raise ValueError(
        "Conversão '%s' não reconhecida. Opções: default, endianness, word_order, byte_order, swap" % converter
    )


def _apply_write_conversion(words: list[int], converter: str | None) -> list[int]:
    if converter is None:
        converter = "default"

    if converter == "default":
        return _swap_words(words)
    if converter == "endianness":
        return words
    if converter == "word_order":
        return _swap_words(words)
    if converter == "byte_order":
        return _swap_bytes_each(_swap_words(words))
    if converter == "swap":
        return _swap_bytes_each(words)

    raise ValueError(
        "Conversão '%s' não reconhecida. Opções: default, endianness, word_order, byte_order, swap" % converter
    )


def _extract_options(config: list[Any], offset_default: int = -1) -> tuple[int, str | None]:
    if not config:
        return offset_default, None

    options: dict[str, Any] = {}
    for item in config:
        if isinstance(item, dict):
            options.update(item)

    offset = int(options.get("offset", offset_default))
    converter = options.get("converter")
    return offset, converter


def replace_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    elif isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(x) for x in obj]
    return obj

def make_response(status: str, data=None, message=None):
    return {"data": data, "status": status, "message": message}

def validate_connection_params(conexao: dict, contexto: str):
    error_payload = make_response("error", message="Parâmetros de conexão inválidos")

    if not isinstance(conexao, dict):
        logging.error("Parâmetros de conexão ausentes ou inválidos para %s.", contexto)
        return None, None, None, error_payload

    ip = conexao.get("ip")
    port = conexao.get("port", 502)
    timeout = conexao.get("timeout", 10.0)

    if not ip or not isinstance(port, int) or not isinstance(timeout, (int, float)):
        logging.error("Parâmetros de conexão inválidos para %s.", contexto)
        return None, None, None, error_payload

    return ip, port, timeout, None

# -----------------------------------------------------------
# 3 - Funções de leitura
# -----------------------------------------------------------
async def read_real(client, reg: int, offset: int = -1, converter: str | None = None, is_input: bool = False):
    try:
        address = int(reg) + int(offset)
        if is_input:
            rr = await client.read_input_registers(address=address, count=2, slave=1)
        else:
            rr = await client.read_holding_registers(address=address, count=2, slave=1)
            
        if rr.isError():
            raise ValueError("Erro ao ler registro REAL")
        registers = _apply_read_conversion(rr.registers, converter)
        return decode_ieee(word_list_to_long(registers, big_endian=True))
    except Exception as e:
        return f"Erro ao ler REAL reg {reg}: {str(e)}"


async def read_int(client, reg: int, offset: int = -1, converter: str | None = None, is_input: bool = False):
    try:
        address = int(reg) + int(offset)
        if is_input:
            rr = await client.read_input_registers(address=address, count=1, slave=1)
        else:
            rr = await client.read_holding_registers(address=address, count=1, slave=1)
            
        if rr.isError():
            raise ValueError("Erro ao ler registro INT")
        return rr.registers[0]
    except Exception as e:
        return f"Erro ao ler INT reg {reg}: {str(e)}"


async def read_boolean(client, reg: int, offset: int = -1, converter: str | None = None):
    try:
        address = int(reg) + int(offset)
        rr = await client.read_coils(address=address, count=1, slave=1)
        if rr.isError():
            raise ValueError("Erro ao ler registro BOOLEAN")
        return rr.bits[0]
    except Exception as e:
        return f"Erro ao ler BOOLEAN reg {reg}: {str(e)}"

# -----------------------------------------------------------
# 4 - Funções de escrita
# -----------------------------------------------------------
async def write_boolean(client, reg: int, value: bool, offset: int = -1, converter: str | None = None):
    try:
        address = int(reg) + int(offset)
        await client.write_coil(address=address, value=value, slave=1)
    except Exception as e:
        return f"Erro ao escrever BOOLEAN reg {reg}: {str(e)}"


async def write_int(client, reg: int, value: int, offset: int = -1, converter: str | None = None):
    try:
        address = int(reg) + int(offset)
        await client.write_register(address=address, value=value, slave=1)
    except Exception as e:
        return f"Erro ao escrever INT reg {reg}: {str(e)}"


async def write_real(client, reg: int, value: float, offset: int = -1, converter: str | None = None):
    try:
        address = int(reg) + int(offset)
        words = float_to_word_list(value, big_endian=True)
        words = _apply_write_conversion(words, converter)
        await client.write_registers(address=address, values=words, slave=1)
    except Exception as e:
        return f"Erro ao escrever REAL reg {reg}: {str(e)}"

# -----------------------------------------------------------
# 5 - Funções de leitura de CLP
# -----------------------------------------------------------
async def ler_clp(registers: dict[str, list], client: AsyncModbusTcpClient):
    start_time = time.perf_counter()
    
    # 1. Preparar lista plana para ordenação
    items = []
    for nome, config in registers.items():
        base_addr = int(config[0])
        tipo = str(config[1]).upper()
        
        # --- CORREÇÃO AQUI: Extrair e aplicar o offset IMEDIATAMENTE ---
        # Extrai offset e conversor das opções
        offset_val, converter_val = _extract_options(list(config[2:]))
        
        # O endereço real de rede é a base + offset (geralmente -1)
        real_addr = base_addr + offset_val
        
        # Define tamanho em words (registros) e o tipo de leitura Modbus
        size = 2 if "REAL" in tipo else 1 
        is_input = "INPUT" in tipo 
        
        if tipo == "BOOLEAN":
            # Booleanos continuam separados pois usam Coils
            continue
            
        items.append({
            "key": nome, 
            "addr": real_addr,      # Usando o endereço corrigido
            "size": size, 
            "type": tipo, 
            "is_input": is_input,
            "converter": converter_val # Guardamos o conversor para usar depois
        })

    # Ordenar por endereço para identificar vizinhos
    items.sort(key=lambda x: x["addr"])

    # 2. Algoritmo de Agrupamento (Clustering)
    MAX_GAP = 40 
    MAX_COUNT = 120 
    
    blocks = []
    if items:
        current_block = [items[0]]
        block_start = items[0]["addr"]
        block_end = block_start + items[0]["size"]
        
        for item in items[1:]:
            addr = item["addr"]
            size = item["size"]
            
            gap = addr - block_end
            
            if gap <= MAX_GAP and (addr + size - block_start) <= MAX_COUNT and item["is_input"] == current_block[-1]["is_input"]:
                current_block.append(item)
                block_end = addr + size
            else:
                blocks.append(current_block)
                current_block = [item]
                block_start = addr
                block_end = addr + size
        blocks.append(current_block)

    # 3. Executar Leituras Otimizadas
    resultado = {}
    pacotes_enviados = 0
    bytes_uteis = 0

    for block in blocks:
        start = block[0]["addr"]
        # Calcula onde termina o bloco
        last_item_end = block[-1]["addr"] + block[-1]["size"]
        count = last_item_end - start
        
        try:
            # Leitura em Bloco (diferenciando Holding de Input Register)
            if block[0]["is_input"]:
                rr = await client.read_input_registers(address=start, count=count, slave=1)
            else:
                rr = await client.read_holding_registers(address=start, count=count, slave=1)
            pacotes_enviados += 1
            
            if rr.isError():
                logging.error(f"Erro leitura bloco addr={start} count={count}")
                for item in block: resultado[item["key"]] = None
                continue

            # 4. Fatiar e Converter os dados
            for item in block:
                # Onde começa meu dado dentro desse buffer recebido?
                offset_in_block = item["addr"] - start
                
                if "REAL" in item["type"]:
                    # Pega 2 words
                    raw = rr.registers[offset_in_block : offset_in_block + 2]
                    
                    # Aplica a conversão (swap bytes/words) salva anteriormente
                    raw = _apply_read_conversion(raw, item["converter"])
                    
                    val = decode_ieee(word_list_to_long(raw, big_endian=True))
                    resultado[item["key"]] = val
                
                elif "INT" in item["type"]:
                    val = rr.registers[offset_in_block]
                    resultado[item["key"]] = val

        except Exception as e:
            logging.error(f"Erro fatal bloco start={start}: {e}")
            for item in block: resultado[item["key"]] = None

    # 5. Ler Booleanos (Coils) - Mantemos a lógica original para coils
    for nome, config in registers.items():
        if str(config[1]).upper() == "BOOLEAN":
            # Aqui usamos sua função original que já trata o offset internamente
            offset_val, _ = _extract_options(list(config[2:]))
            resultado[nome] = await read_boolean(client, int(config[0]), offset=offset_val)
            pacotes_enviados += 1

    # Logs de Diagnóstico
    duration = time.perf_counter() - start_time
    data_hora = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
    
    # Log ajustado para uma linha só para não poluir
    logging.info(
        f"{data_hora} [PERFORMANCE] Tempo: {duration:.3f}s | Pacotes: {pacotes_enviados*2} | Tags Lidas: {len(resultado)}"
    )
    
    return resultado
# async def ler_clp(registers: dict[str, list], client: AsyncModbusTcpClient):
#     tipos = {
#         "REAL": read_real,
#         "INT": read_int,
#         "BOOLEAN": read_boolean,
#     }
#     start_time = time.perf_counter()
#     pacotes_enviados = 0
#     bytes_uteis = 0

#     resultado: dict[str, Any] = {}

#     for nome, config in registers.items():
#         if not isinstance(config, (list, tuple)) or len(config) < 2:
#             raise ValueError(
#                 f"Registro '{nome}' deve ser uma lista no formato [endereco, tipo, { '{offset, conversor}' }]"
#             )

#         endereco = int(config[0])
#         tipo = str(config[1]).upper()
#         offset, conversor = _extract_options(list(config[2:]))

#         if tipo not in tipos:
#             raise ValueError(
#                 f"Tipo inválido '{tipo}' para '{nome}'. Tipos suportados: {list(tipos.keys())}"
#             )

#         pacotes_enviados += 1
#         # REAL = 4 bytes (2 regs), INT = 2 bytes (1 reg), BOOL = 1 bit
#         bytes_uteis += 4 if "REAL" in str(config[1]) else 2 

#         resultado[nome] = await tipos[tipo](client, endereco, offset, conversor)

#     duration = time.perf_counter() - start_time
#     data_hora = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())

#     logging.info(
#         f"{data_hora}"
#         f"[NETWORK DIAGNOSTIC] Requisição completada em {duration:.3f}s. "
#         f"Pacotes trocados (Ida/Volta): {pacotes_enviados * 2}. "
#         f"Payload útil: {bytes_uteis} bytes. "
#         f"Eficiência: {bytes_uteis / (pacotes_enviados * 60):.4f} (Estimado)" # 60 bytes é o tamanho min de um frame TCP
#     )

#     return resultado

# -----------------------------------------------------------
# 6 - Funções de escrita de CLP
# -----------------------------------------------------------
async def write_clp(registers: dict[str, list], client: AsyncModbusTcpClient):
    tipos = {
        "BOOLEAN": write_boolean,
        "INT": write_int,
        "REAL": write_real,
    }

    resultado: dict[str, Any] = {}

    for nome, config in registers.items():
        if not isinstance(config, (list, tuple)) or len(config) < 3:
            raise ValueError(
                f"Registro '{nome}' deve ser uma lista no formato [endereco, tipo, valor, {{offset, conversor}}]"
            )

        endereco = int(config[0])
        tipo = str(config[1]).upper()
        valor = config[2]
        offset, conversor = _extract_options(list(config[3:]))

        if tipo not in tipos:
            raise ValueError(
                f"Tipo inválido '{tipo}' para '{nome}'. Tipos suportados: {list(tipos.keys())}"
            )

        resultado[nome] = await tipos[tipo](client, endereco, valor, offset, conversor)

    return resultado

# -----------------------------------------------------------
# 7 - Conexão Modbus
# -----------------------------------------------------------
async def get_modbus_client(ip: str, port: int, timeout: float = 10.0) -> AsyncModbusTcpClient:
    # Garantir que modbus_clients esteja inicializado
    if not hasattr(app.state, "modbus_clients"):
        app.state.modbus_clients = {}
        app.state.modbus_last_used = {}

    client_key = f"{ip}:{port}"
    current_time = time.time()

    client = app.state.modbus_clients.get(client_key)
    if client and client.connected:
        app.state.modbus_last_used[client_key] = current_time
        app.state.modbus_usage_count += 1
        logging.debug(
            "Conexão Modbus reutilizada: %s (uso #%s)",
            client_key,
            app.state.modbus_usage_count,
        )
        return client

    if client and not client.connected:
        client.close()
        del app.state.modbus_clients[client_key]
        app.state.modbus_last_used.pop(client_key, None)

    client = AsyncModbusTcpClient(ip, port=port, timeout=timeout, retries=5)

    try:
        await client.connect()
        if not client.connected:
            raise RuntimeError(f"(sem conexão)")
    except (ModbusException, asyncio.TimeoutError, OSError, RuntimeError) as exc:
        client.close()
        logging.error("Falha ao conectar em %s: %s (%s)", client_key, exc, type(exc).__name__)
        raise RuntimeError(f"Falha ao conectar em {client_key}: {exc}") from exc
    except Exception as exc:
        client.close()
        logging.error("Erro inesperado ao conectar em %s: %s (%s)", client_key, exc, type(exc).__name__)
        raise RuntimeError(f"Erro inesperado ao conectar em {client_key}: {exc}") from exc

    app.state.modbus_clients[client_key] = client
    app.state.modbus_last_used[client_key] = current_time
    app.state.active_connection_count += 1
    app.state.modbus_usage_count += 1

    logging.info(
        "Conexão Modbus ativa: %s (ativas: %s, total criadas: %s, usos totais: %s)",
        client_key,
        len(app.state.modbus_clients),
        app.state.active_connection_count,
        app.state.modbus_usage_count,
    )
    logging.debug(
        "Conexões Modbus atuais: %s | usos totais: %s",
        list(app.state.modbus_clients.keys()),
        app.state.modbus_usage_count,
    )

    return app.state.modbus_clients[client_key]

async def close_modbus_client(ip: str, port: int):
    client_key = f"{ip}:{port}"
    client = app.state.modbus_clients.get(client_key)
    if client:
        client.close()
        del app.state.modbus_clients[client_key]
        app.state.modbus_last_used.pop(client_key, None)
        logging.info(
            "Conexão Modbus fechada: %s (ativas restantes: %s, usos totais: %s)",
            client_key,
            len(app.state.modbus_clients),
            app.state.modbus_usage_count,
        )
        logging.debug(
            "Conexões Modbus atuais: %s",
            list(app.state.modbus_clients.keys()),
        )


async def cleanup_idle_connections(app: FastAPI):
    try:
        while True:
            try:
                await asyncio.wait_for(app.state.stop_cleanup.wait(), timeout=CLEANUP_INTERVAL_SECONDS)
                break
            except asyncio.TimeoutError:
                if not hasattr(app.state, "modbus_clients"):
                    continue

                now = time.time()
                if app.state.modbus_clients:
                    logging.debug(
                        "Verificando conexões inativas: %s",
                        list(app.state.modbus_clients.keys()),
                    )

                idle_keys = []

                for key, last_used in app.state.modbus_last_used.items():
                    if now - last_used > IDLE_TIMEOUT_SECONDS:
                        idle_keys.append((key, last_used))

                for key, last_used in idle_keys:
                    client = app.state.modbus_clients.pop(key, None)
                    app.state.modbus_last_used.pop(key, None)

                    if client:
                        client.close()
                        logging.info(
                            "Conexão Modbus fechada por inatividade (%.1fs): %s (ativas restantes: %s, usos totais: %s)",
                            now - last_used,
                            key,
                            len(app.state.modbus_clients),
                            app.state.modbus_usage_count,
                        )
                        logging.debug(
                            "Conexões restantes após cleanup: %s | usos totais: %s",
                            list(app.state.modbus_clients.keys()),
                            app.state.modbus_usage_count,
                        )
    except asyncio.CancelledError:
        pass

# -----------------------------------------------------------
# 8 - Configuração do FastAPI e Gerenciamento de lifespan
# -----------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização
    app.state.modbus_clients = {}
    app.state.modbus_last_used = {}  # Rastrear última utilização
    app.state.active_connection_count = 0
    app.state.modbus_usage_count = 0
    app.state.stop_cleanup = asyncio.Event()
    app.state.cleanup_task = asyncio.create_task(cleanup_idle_connections(app))

    try:
        yield
    finally:
        app.state.stop_cleanup.set()
        try:
            await app.state.cleanup_task
        except asyncio.CancelledError:
            pass

    # Encerramento
    if hasattr(app.state, "modbus_clients"):
        for client_key, client in app.state.modbus_clients.items():
            client.close()
            logging.info(f"Conexão Modbus fechada (encerramento app): {client_key}")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# 9 - Endpoints
# -----------------------------------------------------------
@app.post("/writeCLP/{tipo}")
async def write_clp_endpoint(tipo: str, conexao: dict, registers: dict):
    if tipo not in ["reset_alarmes_automatico","escritas"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'alarmes'.")

    ip, port, timeout, error_response = validate_connection_params(conexao, "escrita")
    if error_response:
        return error_response
    try:
        client = await get_modbus_client(ip, port, timeout)
    except Exception as exc:
        logging.error("Falha ao conectar em %s:%s para escrita: %s (%s)", ip, port, exc, type(exc).__name__)
        return make_response("error", message=str(exc))

    try:
        result = await write_clp(registers, client)
        return make_response("success", data=result)
    except Exception as exc:
        await close_modbus_client(ip, port)
        logging.error("Erro ao escrever CLP em %s:%s: %s (%s)", ip, port, exc, type(exc).__name__)
        return make_response("error", message=f"Erro ao escrever CLP: {exc}")

@app.post("/readCLP/{tipo}")
async def read_clp_endpoint(tipo: str, conexao: dict, registers: dict):
    if tipo not in ["leituras", "alarmes"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'leituras' ou 'alarmes'.")

    ip, port, timeout, error_response = validate_connection_params(conexao, "leitura")
    if error_response:
        return error_response

    try:
        client = await get_modbus_client(ip, port, timeout)
    except Exception as exc:
        logging.error("Falha ao conectar em %s:%s para leitura: %s (%s)", ip, port, exc, type(exc).__name__)
        return make_response("error", message=str(exc))

    try:
        result = await ler_clp(registers, client)
        result = replace_nan(result)
        return make_response("success", data=result)
    except Exception as exc:
        await close_modbus_client(ip, port)
        logging.error("Erro ao ler CLP em %s:%s: %s (%s)", ip, port, exc, type(exc).__name__)
        return make_response("error", message=f"Erro ao ler CLP: {exc}")

@app.get("/listConnections")
async def list_connections_endpoint():
    """
    Lista todas as conexões Modbus ativas.
    """
    if not hasattr(app.state, "modbus_clients"):
        return make_response("success", data={"active_connections": []}, message="Nenhuma conexão ativa")
    
    active_connections = []
    current_time = time.time()
    
    for client_key, client in app.state.modbus_clients.items():
        last_used = app.state.modbus_last_used.get(client_key, 0)
        idle_time = current_time - last_used
        
        active_connections.append({
            "connection": client_key,
            "connected": client.connected,
            "last_used": last_used,
            "idle_time_seconds": round(idle_time, 2)
        })
    
    return make_response("success", data={"active_connections": active_connections}, message=f"{len(active_connections)} conexões ativas encontradas")

@app.post("/closeConnections")
async def close_connections_endpoint():
    if not hasattr(app.state, "modbus_clients"):
        return make_response("success", data={"closed_connections": []}, message="Nenhuma conexão ativa encontrada")

    closed_connections = []

    for client_key, client in app.state.modbus_clients.items():
        client.close()
        closed_connections.append(client_key)
        logging.info(f"Conexão Modbus fechada via endpoint: {client_key}")

    app.state.modbus_clients.clear()
    app.state.modbus_last_used.clear()

    return make_response("success", data={"closed_connections": closed_connections}, message=f"{len(closed_connections)} conexões fechadas com sucesso")



@app.get("/diagnostics")
async def diagnostics_endpoint(log_lines: int = 50):
    """
    Retorna saúde do sistema: conexões Modbus ativas e as últimas linhas de log.
    Query param: ?log_lines=50 (Padrão 50 linhas)
    """
    
    # 1. Coleta das Conexões
    active_connections = []
    if hasattr(app.state, "modbus_clients"):
        current_time = time.time()
        for client_key, client in app.state.modbus_clients.items():
            last_used = app.state.modbus_last_used.get(client_key, 0)
            idle_time = current_time - last_used
            
            active_connections.append({
                "connection": client_key,
                "connected": client.connected,
                "last_used": last_used,
                "idle_time_seconds": round(idle_time, 2)
            })

    # 2. Coleta dos Logs (Execução em thread para não bloquear loop)
    def read_logs_tail(file_path: str, lines: int) -> list[str]:
        if not os.path.exists(file_path):
            return ["Arquivo de log não encontrado."]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in deque(f, maxlen=lines)]
        except Exception as e:
            return [f"Erro ao ler logs: {str(e)}"]

    loop = asyncio.get_running_loop()
    recent_logs = await loop.run_in_executor(None, read_logs_tail, LOG_FILE, log_lines)

    # 3. Montagem da Resposta
    return make_response(
        "success", 
        data={
            "server_timestamp": time.time(),
            "active_connections_count": len(active_connections),
            "connections": active_connections,
            "logs": recent_logs
        }, 
        message="Diagnóstico realizado com sucesso"
    )

# -----------------------------------------------------------
# 7 - Inicialização do servidor
# -----------------------------------------------------------
if __name__ == "__main__":
    try:
        config = uvicorn.Config(
            app=app,
            host=IP_API,
            port=int(PORT_API),
            log_level=None,
            access_log=False,
            use_colors=False,
            workers=1
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        logging.error(f"Erro ao iniciar o servidor: {str(e)}")
        # total 397, 355, 348, 324, 375, 333-> linhas de codigo

