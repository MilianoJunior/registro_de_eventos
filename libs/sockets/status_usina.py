"""Handlers e utilitários para status operacional das usinas via Socket.IO."""

import asyncio
import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:  # pragma: no cover - fallback para ambientes sem flask_socketio
    from flask_socketio import emit
except ImportError:  # pragma: no cover
    emit = None  # type: ignore

from libs.servicos.readRT import get_data

DEBUG_PREFIX = "[DEBUG][status_usina]"

CONFIG_PATH = Path("config/usinas_dispositivos.json")
DEFAULT_TIMEOUT = 3.0

# prioridade para consolidar status vindos de diferentes dispositivos
STATUS_PRIORITY = {
    "operando": 3,
    "manutencao": 2,
    "parada": 1,
}

# ordem de prioridade para definir a descrição textual enviada ao front
STATUS_LABEL_ORDER = [
    "Status U.M.D.(sincronizado)",
    "Status sincronizado",
    "Status U.P.S.(pronta para sincronização)",
    "Status U.P.G.M. (pronta para giro mecânico)",
    "Status U.P. (parada)",
]

# palavras-chave usadas para interpretar os registradores BOOLEAN
OPERANDO_TAGS = ("sincronizado",)
MANUTENCAO_TAGS = ("prontaparasincronizacao", "prontaparagiro")
PARADA_TAGS = ("parada",)


def register_status_usina_handler(socketio):
    """Registra o handler responsável por atualizar o status operacional das usinas."""
    
    contador_solicitacoes = {"total": 0, "ultima_timestamp": 0}

    @socketio.on("solicitar_status_usinas")
    def handle_status_usinas(_payload=None):
        """Lê o status operacional no CLP e envia o resultado para os clientes conectados."""
        if emit is None:
            print("[SOCKET][status_usina] flask_socketio não disponível; ignorando emissão.")  # noqa: T201
            return

        # Verificar frequência de solicitações
        agora = time.time()
        contador_solicitacoes["total"] += 1
        diferenca = agora - contador_solicitacoes["ultima_timestamp"] if contador_solicitacoes["ultima_timestamp"] > 0 else 0
        contador_solicitacoes["ultima_timestamp"] = agora
        
        print(f"\n{DEBUG_PREFIX} Evento 'solicitar_status_usinas' recebido.")
        print(f"{DEBUG_PREFIX} Solicitação #{contador_solicitacoes['total']} | Intervalo desde última: {diferenca:.2f}s")
        
        if diferenca > 0 and diferenca < 5:
            print(f"{DEBUG_PREFIX} ⚠️ ALERTA: Solicitações muito próximas ({diferenca:.2f}s)! Possível duplicação.")
        
        payload = build_status_payload()
        _imprimir_payload_organizado(payload)
        emit("status_usinas_dados", payload, broadcast=True)


def build_status_payload() -> Dict[str, Any]:
    """Monta o payload enviado para o front-end com os status operacionais."""
    try:
        usinas = coletar_status_usinas()
        return {
            "success": True,
            "timestamp": time.time(),
            "usinas": usinas,
        }
    except FileNotFoundError as exc:
        print(f"{DEBUG_PREFIX} Arquivo de configuração não encontrado: {exc}")
        return {
            "success": False,
            "error": str(exc),
            "usinas": [],
        }
    except Exception as exc:  # pragma: no cover - log auxiliar
        print(f"[SOCKET][status_usina] Erro ao montar payload: {exc}")  # noqa: T201
        return {
            "success": False,
            "error": str(exc),
            "usinas": [],
        }


def coletar_status_usinas() -> List[Dict[str, Any]]:
    """Obtém o status operacional consolidado de todas as usinas configuradas."""
    configuracoes = _carregar_configuracoes()
    if not configuracoes:
        print(f"{DEBUG_PREFIX} Nenhuma configuração encontrada.")
        return []

    print(f"{DEBUG_PREFIX} Configurações carregadas: {list(configuracoes.keys())}")
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_coletar_status_async(configuracoes))
    finally:
        loop.close()
        asyncio.set_event_loop(None)


def _carregar_configuracoes() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado em '{CONFIG_PATH.as_posix()}'."
        )

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        configuracoes = json.load(config_file)
        print(f"{DEBUG_PREFIX} Conteúdo do arquivo de configuração carregado.")
        return configuracoes


async def _coletar_status_async(configuracoes: Dict[str, Any]) -> List[Dict[str, Any]]:
    tarefas = []

    for nome_usina, dados_usina in configuracoes.items():
        dispositivos = (dados_usina or {}).get("dispositivos") or {}
        for nome_dispositivo, dados_dispositivo in dispositivos.items():
            tarefas.append(
                _ler_status_dispositivo(
                    nome_usina,
                    dados_usina,
                    nome_dispositivo,
                    dados_dispositivo,
                )
            )

    if not tarefas:
        return []

    resultados = await asyncio.gather(*tarefas, return_exceptions=True)
    consolidados: Dict[str, Dict[str, Any]] = {}

    for resultado in resultados:
        if isinstance(resultado, Exception):
            print(f"[SOCKET][status_usina] Erro ao ler dispositivo: {resultado}")  # noqa: T201
            continue

        slug = resultado["usina_slug"]
        entrada = consolidados.setdefault(
            slug,
            {
                "nome": resultado["usina_nome"],
                "slug": slug,
                "status": "parada",
                "status_texto": "Status não disponível",
                "dispositivos": [],
            },
        )

        entrada["dispositivos"].append(
            {
                "nome": resultado["dispositivo_nome"],
                "status": resultado["status"],
                "valores": resultado["valores"],
                "descricao": resultado["descricao"],
                "tempo_leitura": resultado["tempo_leitura"],
                "erro": resultado.get("erro"),
            }
        )

        status_atual = entrada["status"]
        status_calculado = resultado["status"]
        novo_status = _priorizar_status(status_atual, status_calculado)
        if novo_status != status_atual or entrada.get("status_texto") in (None, "Status não disponível"):
            entrada["status_texto"] = resultado.get("descricao") or entrada.get("status_texto")
        entrada["status"] = novo_status

    return sorted(consolidados.values(), key=lambda item: item["nome"])


async def _ler_status_dispositivo(
    nome_usina: str,
    dados_usina: Dict[str, Any],
    nome_dispositivo: str,
    dados_dispositivo: Dict[str, Any],
) -> Dict[str, Any]:
    slug_usina = _normalizar_chave(nome_usina)
    conexao = (dados_dispositivo or {}).get("conexao") or {}

    if not conexao.get("ip") or not conexao.get("port"):
        print(
            f"{DEBUG_PREFIX} Conexão ausente para usina='{nome_usina}', dispositivo='{nome_dispositivo}'."
        )
        return {
            "usina_nome": nome_usina,
            "usina_slug": slug_usina,
            "dispositivo_nome": nome_dispositivo,
            "status": "parada",
            "valores": {},
            "tempo_leitura": 0.0,
            "erro": "Dados de conexão ausentes.",
        }

    registradores_boolean = _extrair_registradores_boolean(dados_dispositivo)
    if not registradores_boolean:
        print(
            f"{DEBUG_PREFIX} Nenhum registrador BOOLEAN configurado para "
            f"usina='{nome_usina}', dispositivo='{nome_dispositivo}'."
        )
        return {
            "usina_nome": nome_usina,
            "usina_slug": slug_usina,
            "dispositivo_nome": nome_dispositivo,
            "status": "parada",
            "valores": {},
            "tempo_leitura": 0.0,
            "erro": "Nenhum registrador BOOLEAN configurado.",
        }

    config_api = {
        "ip": dados_usina.get("ip"),
        "port": dados_usina.get("port"),
        "tipo": "leituras",
    }

    dados_leitura = {
        "conexao": {
            "ip": conexao.get("ip"),
            "port": conexao.get("port"),
            "timeout": conexao.get("timeout", DEFAULT_TIMEOUT),
        },
        "leituras": {
            "BOOLEAN": registradores_boolean,
        },
    }

    try:
        resultado, tempo = await get_data(config_api, dados_leitura)
    except Exception as exc:
        return {
            "usina_nome": nome_usina,
            "usina_slug": slug_usina,
            "dispositivo_nome": nome_dispositivo,
            "status": "parada",
            "valores": {},
            "tempo_leitura": 0.0,
            "erro": str(exc),
        }

    valores_boolean = {}
    if isinstance(resultado, dict):
        valores_boolean = resultado.get("BOOLEAN") or {}

    status = _determinar_status(valores_boolean)
    descricao = _obter_label_status(valores_boolean)

    return {
        "usina_nome": nome_usina,
        "usina_slug": slug_usina,
        "dispositivo_nome": nome_dispositivo,
        "status": status,
        "valores": valores_boolean,
        "descricao": descricao,
        "tempo_leitura": tempo,
        "erro": None,
    }


def _extrair_registradores_boolean(dados_dispositivo: Dict[str, Any]) -> Dict[str, Any]:
    leituras = (dados_dispositivo or {}).get("leituras") or {}
    booleanos = leituras.get("BOOLEAN") or {}
    return dict(booleanos)


def _priorizar_status(atual: str, novo: str) -> str:
    prioridade_atual = STATUS_PRIORITY.get(atual, 0)
    prioridade_novo = STATUS_PRIORITY.get(novo, 0)
    return novo if prioridade_novo > prioridade_atual else atual


def _determinar_status(valores: Dict[str, Any]) -> str:
    if not valores:
        return "parada"

    normalizados = {
        _normalizar_chave(chave): _converter_bool(valor)
        for chave, valor in valores.items()
    }

    if _possui_tag_ativa(normalizados, OPERANDO_TAGS):
        return "operando"

    if _possui_tag_ativa(normalizados, MANUTENCAO_TAGS):
        return "manutencao"

    if _possui_tag_ativa(normalizados, PARADA_TAGS):
        return "parada"

    return "parada"


def _converter_bool(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return False
    if isinstance(valor, (int, float)):
        return valor != 0
    texto = str(valor).strip().lower()
    return texto in {"1", "true", "t", "sim", "on"}


def _normalizar_chave(texto: Optional[str]) -> str:
    if texto is None:
        return ""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(char for char in normalizado if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]", "", sem_acentos.lower())


def _possui_tag_ativa(valores: Dict[str, bool], tags: Iterable[str]) -> bool:
    return any(
        ativo and any(tag in chave for tag in tags)
        for chave, ativo in valores.items()
    )


def _obter_label_status(valores: Dict[str, Any]) -> str:
    for label in STATUS_LABEL_ORDER:
        chave_alvo = _normalizar_chave(label)
        for chave, valor in valores.items():
            if _normalizar_chave(chave) == chave_alvo and bool(valor):
                return chave
    # se nenhuma das chaves conhecidas estiver presente/true,
    # tenta retornar a primeira chave verdadeira disponível
    for chave, ativo in valores.items():
        if bool(ativo):
            return chave
    return "Status U.P. (parada)"


def _imprimir_payload_organizado(payload: Dict[str, Any]) -> None:
    """Imprime o payload de forma organizada, separando por usina."""
    print("\n" + "="*80)
    print("📡 PAYLOAD DE STATUS DAS USINAS".center(80))
    print("="*80)
    
    if not payload.get("success"):
        print(f"❌ Erro: {payload.get('error', 'Erro desconhecido')}")
        print("="*80 + "\n")
        return
    
    usinas = payload.get("usinas", [])
    if not usinas:
        print("⚠️  Nenhuma usina encontrada")
        print("="*80 + "\n")
        return
    
    print(f"✅ Total de usinas: {len(usinas)}")
    print(f"🕐 Timestamp: {time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(payload.get('timestamp', 0)))}")
    print("="*80)
    
    for idx, usina in enumerate(usinas, 1):
        nome = usina.get("nome", "N/A")
        slug = usina.get("slug", "N/A")
        status = usina.get("status", "N/A").upper()
        status_texto = usina.get("status_texto", "N/A")
        dispositivos = usina.get("dispositivos", [])
        
        # Ícones por status
        icone_status = {
            "OPERANDO": "🟢",
            "MANUTENCAO": "🟡",
            "PARADA": "🔴",
        }.get(status, "⚪")
        
        print(f"\n{icone_status} [{idx}] {nome}")
        print(f"    Slug: {slug}")
        print(f"    Status Geral: {status} → {status_texto}")
        print(f"    Dispositivos: {len(dispositivos)}")
        
        if dispositivos:
            print(f"    " + "-"*72)
            for disp_idx, disp in enumerate(dispositivos, 1):
                disp_nome = disp.get("nome", "N/A")
                disp_status = disp.get("status", "N/A").upper()
                disp_descricao = disp.get("descricao", "N/A")
                disp_tempo = disp.get("tempo_leitura", 0)
                disp_erro = disp.get("erro")
                
                # Ícone do dispositivo
                icone_disp = {
                    "OPERANDO": "✅",
                    "MANUTENCAO": "⚠️",
                    "PARADA": "❌",
                }.get(disp_status, "❓")
                
                print(f"    {icone_disp} [{disp_idx}] {disp_nome}")
                print(f"        Status: {disp_status}")
                print(f"        Descrição: {disp_descricao}")
                print(f"        Tempo de leitura: {disp_tempo:.3f}s")
                
                if disp_erro:
                    print(f"        ⚠️ Erro: {disp_erro}")
                
                # Mostrar valores booleanos se houver
                valores = disp.get("valores", {})
                if valores:
                    print(f"        Valores:")
                    for chave, valor in valores.items():
                        simbolo = "✓" if valor else "✗"
                        print(f"          {simbolo} {chave}: {valor}")
                
                if disp_idx < len(dispositivos):
                    print(f"        " + "·"*68)
        else:
            print(f"    ⚠️  Nenhum dispositivo configurado")
    
    print("\n" + "="*80 + "\n")


__all__ = [
    "register_status_usina_handler",
    "coletar_status_usinas",
    "build_status_payload",
]
