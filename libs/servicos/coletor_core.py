# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. coletar_status_completo → orquestra coleta completa (entry point)
# 2. _carregar_configuracoes → lê JSON de configuração
# 3. get_dados_cache → busca cache ou executa leitura real
# 4. registrar_intervencao → registra intervenção manual e persiste em JSON
# 5. _carregar_intervencoes → carrega intervenções persistidas do JSON
# 6. _salvar_intervencoes → salva intervenções em JSON (atômico)
# 7. _coletar_async → cria tarefas paralelas por dispositivo
# 8. _ler_dispositivo → lê status/potência de um dispositivo
# 9. _extrair_registradores_status → filtra registradores de status
# 10. _extrair_registradores_potencia → filtra registradores de potência
# 11. _determinar_status → determina status geral da UG
# 12. _normalizar_slug → normaliza nome para slug
# -------------------------------------------------------------------

import asyncio
import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional
from threading import Lock

from libs.servicos.readRT import get_data
from libs.controllers.decorador import desempenho

# -------------------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------------------
CONFIG_PATH = Path("config/usinas_dispositivos.json")
INTERVENCOES_PATH = Path("config/intervencoes_operador.json")
DEFAULT_TIMEOUT = 3.0

STATUS_LABEL_ORDER = [
    "US (sincronizado)",
    "UMD (marcha desexcitada)",
    "UPS (pronta para sincronização)",
    "UPGM (pronta para giro mecânico)",
    "UP (parada)",
]

POTENCIA_LABELS = ["Potência Ativa"]

# -------------------------------------------------------------------
# CACHE GLOBAL (compartilhado entre thread e socket)
# -------------------------------------------------------------------
_cache_leituras: Dict[str, tuple] = {}  # {chave: (payload, timestamp)}
CACHE_TTL_SEGUNDOS = 5  # cache válido por 5 segundos
_lock_intervencoes = Lock()
_lock_config = Lock()
_config_cache: Dict[str, Any] = {"mtime": None, "data": None}

def get_dados_cache(chave: str, func_coleta, *args, **kwargs):
    agora = time.time()
    
    if chave in _cache_leituras:
        payload_cache, timestamp_cache = _cache_leituras[chave]
        if agora - timestamp_cache < CACHE_TTL_SEGUNDOS:
            print(f"[CACHE] Retornando dados em cache para '{chave}' (idade: {agora - timestamp_cache:.1f}s)")
            return payload_cache

    payload = func_coleta(*args, **kwargs)
    _cache_leituras[chave] = (payload, agora)
    return payload
# -------------------------------------------------------------------
# ESTADO GLOBAL DE INTERVENÇÕES
# Armazena intervenções manuais: { 'slug_usina': { 'nome_disp': 'MOTIVO' } }
# -------------------------------------------------------------------
INTERVENCOES_GLOBAIS: Dict[str, Dict[str, str]] = {}

@desempenho
def _carregar_intervencoes() -> Dict[str, Dict[str, str]]:
    try:
        if not INTERVENCOES_PATH.exists():
            return {}
        with INTERVENCOES_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        out: Dict[str, Dict[str, str]] = {}
        for usina_slug, dispositivos in data.items():
            if not isinstance(usina_slug, str) or not isinstance(dispositivos, dict):
                continue
            out[usina_slug] = {
                str(nome_disp): str(motivo)
                for nome_disp, motivo in dispositivos.items()
                if motivo in ("MANUTENCAO", "RESTRICAO")
            }
        return {k: v for k, v in out.items() if v}
    except Exception as e:
        print(f"[ERRO][coletor_core] Falha ao carregar intervenções: {e}")
        return {}

@desempenho
def _salvar_intervencoes(intervencoes: Dict[str, Dict[str, str]]) -> None:
    try:
        INTERVENCOES_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = INTERVENCOES_PATH.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(intervencoes, f, ensure_ascii=False, indent=2, sort_keys=True)
        tmp.replace(INTERVENCOES_PATH)
    except Exception as e:
        print(f"[ERRO][coletor_core] Falha ao salvar intervenções: {e}")

# Carrega intervenções persistidas ao iniciar o módulo (sobrevive a refresh/restart)
INTERVENCOES_GLOBAIS.update(_carregar_intervencoes())

def registrar_intervencao(usina_slug: str, dispositivo_nome: str, motivo: str):
    """Registra ou remove uma intervenção manual no estado global."""
    if not usina_slug or not dispositivo_nome or not motivo:
        return

    with _lock_intervencoes:
        if motivo == "NORMAL":
            if usina_slug in INTERVENCOES_GLOBAIS:
                INTERVENCOES_GLOBAIS[usina_slug].pop(dispositivo_nome, None)
                if not INTERVENCOES_GLOBAIS[usina_slug]:
                    del INTERVENCOES_GLOBAIS[usina_slug]
        elif motivo in ("MANUTENCAO", "RESTRICAO"):
            if usina_slug not in INTERVENCOES_GLOBAIS:
                INTERVENCOES_GLOBAIS[usina_slug] = {}
            INTERVENCOES_GLOBAIS[usina_slug][dispositivo_nome] = motivo
        else:
            return

        _salvar_intervencoes(INTERVENCOES_GLOBAIS)

        # Força refletir o override imediatamente após intervenção (evita TTL do cache)
        _cache_leituras.pop("coleta_completa", None)

def coletar_status_completo(intervencoes_externas: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        usinas = _coletar_status_usinas(INTERVENCOES_GLOBAIS)
        return {
            "success": True,
            "timestamp": time.time(),
            "usinas": usinas,
        }
    except Exception as exc:
        print(f"[ERRO][coletor_core] Erro ao coletar status: {exc}")
        return {
            "success": False,
            "error": str(exc),
            "usinas": [],
        }

def _coletar_status_usinas(intervencoes_externas: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Carrega configs e executa coleta async."""
    configuracoes = _carregar_configuracoes()
    
    if not configuracoes:
        print("[WARN][coletor_core] Nenhuma configuração carregada.")
        return []
    
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_coletar_async(configuracoes, intervencoes_externas))
    finally:
        loop.close()
        asyncio.set_event_loop(None)

@desempenho
def _carregar_configuracoes() -> Dict[str, Any]:
    """Lê arquivo JSON de configuração das usinas."""
    try:
        if not CONFIG_PATH.exists():
            print(f"[ERRO][coletor_core] Arquivo não encontrado: {CONFIG_PATH}")
            return {}

        mtime = CONFIG_PATH.stat().st_mtime
        with _lock_config:
            if _config_cache.get("mtime") == mtime and isinstance(_config_cache.get("data"), dict):
                return _config_cache["data"]

        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {}

        with _lock_config:
            _config_cache["mtime"] = mtime
            _config_cache["data"] = data
        return data
    except json.JSONDecodeError as e:
        print(f"[ERRO][coletor_core] Erro ao parsear JSON: {e}")
    except Exception as e:
        print(f"[ERRO][coletor_core] Erro inesperado: {e}")
    return {}

async def _coletar_async(configuracoes: Dict[str, Any], intervencoes_externas: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Cria tarefas async paralelas para cada dispositivo."""
    tarefas = []
    intervencoes_externas = intervencoes_externas or {}
    
    for nome_usina, dados_usina in configuracoes.items():
        dispositivos = (dados_usina or {}).get("dispositivos") or {}
        for nome_dispositivo, dados_dispositivo in dispositivos.items():
            tarefas.append(
                _ler_dispositivo(
                    nome_usina,
                    dados_usina,
                    nome_dispositivo,
                    dados_dispositivo,
                    intervencoes_externas
                )
            )
    
    resultados = await asyncio.gather(*tarefas, return_exceptions=True)
    
    # Consolida por usina
    consolidados: Dict[str, Dict[str, Any]] = {}
    
    for resultado in resultados:
        if isinstance(resultado, Exception):
            print(f"[ERRO][coletor_core] Erro ao ler dispositivo: {resultado}")
            continue
        
        usina_nome = resultado["usina_nome"]
        usina_slug = resultado["usina_slug"]
        dispositivo_nome = resultado["dispositivo_nome"]
        
        entrada_usina = consolidados.setdefault(
            usina_slug,
            {
                "nome": usina_nome,
                "slug": usina_slug,
                "dispositivos": {},
            },
        )
        
        entrada_usina["dispositivos"][dispositivo_nome] = {
            "nome": dispositivo_nome,
            "potencia_ativa_mw": resultado["potencia_ativa_mw"],
            "descricao": resultado["descricao"],
            "tempo_leitura": resultado["tempo_leitura"],
            "erro": resultado["erro"],
        }
    
    return sorted(consolidados.values(), key=lambda item: item["nome"])

async def _ler_dispositivo(
    nome_usina: str,
    dados_usina: Dict[str, Any],
    nome_dispositivo: str,
    dados_dispositivo: Dict[str, Any],
    intervencoes_externas: Dict[str, Any]
) -> Dict[str, Any]:
    """Lê status e potência de um dispositivo via Modbus."""
    slug_usina = _normalizar_slug(nome_usina)
    conexao = (dados_dispositivo or {}).get("conexao") or {}
    
    registradores_status = _extrair_registradores_status(dados_dispositivo)
    registradores_potencia = _extrair_registradores_potencia(dados_dispositivo)
    registradores_leitura = {**registradores_status, **registradores_potencia}
    
    if not registradores_status:
        print(f"[WARN][coletor_core] Sem registradores STATUS: {nome_usina}/{nome_dispositivo}")
        return _dict_response(
            nome_usina, slug_usina, nome_dispositivo, 0.0, "Sem conexão", 0.0,
            "Nenhum registrador de STATUS configurado."
        )
    
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
        "registers": registradores_leitura,
    }
    
    try:
        resultado, tempo, erro = await get_data(config_api, dados_leitura, nome_usina, nome_dispositivo)
    except Exception as exc:
        erro_str = str(exc)
        print(f"[ERRO][coletor_core] Falha leitura {nome_usina}/{nome_dispositivo}: {erro_str}")
        
        return _dict_response(
            nome_usina, slug_usina, nome_dispositivo, 0.0, "Sem conexão", 0.0, erro_str
        )
    
    if resultado is None:
        return _dict_response(
            nome_usina, slug_usina, nome_dispositivo, 0.0, "Sem conexão", tempo, erro
        )
    
    valores_status = {
        chave: resultado.get(chave)
        for chave in STATUS_LABEL_ORDER
        if chave in resultado
    }
    
    status_real = _determinar_status(valores_status, nome_usina, nome_dispositivo)
    descricao_final = status_real

    # LÓGICA DE OVERRIDE DE INTERVENÇÃO MANUAL
    if status_real == "UP (parada)":
        intervencao_usina = intervencoes_externas.get(slug_usina, {})
        motivo_override = intervencao_usina.get(nome_dispositivo)
        
        if motivo_override == "MANUTENCAO":
            descricao_final = "Manutenção (parada)"
        elif motivo_override == "RESTRICAO":
            descricao_final = "Restrição da concessionária (parada)"

    potencia_ativa_mw = _extrair_potencia_ativa(resultado)
    
    return _dict_response(
        nome_usina, slug_usina, nome_dispositivo,
        potencia_ativa_mw or 0.0, descricao_final, tempo, erro
    )

# -------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------------------------------------------

def _extrair_registradores_status(dados_dispositivo: Dict[str, Any]) -> Dict[str, Any]:
    """Filtra apenas registradores de status (BOOLEAN)."""
    leituras = (dados_dispositivo or {}).get("leituras") or {}
    registradores: Dict[str, Any] = {}
    
    for status_ug in STATUS_LABEL_ORDER:
        config = leituras.get(status_ug)
        if isinstance(config, list) and len(config) >= 2 and config[1] == "BOOLEAN":
            registradores[status_ug] = config
    return registradores

def _extrair_registradores_potencia(dados_dispositivo: Dict[str, Any]) -> Dict[str, Any]:
    """Filtra apenas registradores de potência."""
    leituras = (dados_dispositivo or {}).get("leituras") or {}
    registradores: Dict[str, Any] = {}
    
    for label in POTENCIA_LABELS:
        config = leituras.get(label)
        if isinstance(config, list) and len(config) >= 2:
            registradores[label] = config
    return registradores

def _extrair_potencia_ativa(valores: Optional[Dict[str, Any]]) -> Optional[float]:
    """Extrai valor float de potência ativa."""
    if not valores:
        return None
    for label in POTENCIA_LABELS:
        if label not in valores:
            continue
        try:
            return float(valores[label])
        except (TypeError, ValueError):
            return None
    return None

def _determinar_status(valores: Dict[str, Any], nome_usina: str, nome_dispositivo: str) -> str:
    """Determina status geral da UG (primeiro True na ordem de prioridade)."""
    for key, val in valores.items():
        if val is True:
            return key
    # raise ValueError(f"Nome da usina: {nome_usina}, Nome do dispositivo: {nome_dispositivo}, Status indeterminado: {valores}")
    return "Indeterminado"

def _normalizar_slug(texto: str) -> str:
    """Normaliza texto para slug (sem acentos, minúsculo, alfanumérico)."""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(
        char for char in normalizado if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9]", "", sem_acentos.lower())

def _dict_response(
    nome_usina: str,
    slug_usina: str,
    nome_dispositivo: str,
    potencia_ativa_mw: float,
    descricao: str,
    tempo_leitura: float,
    erro: Optional[Any],
) -> Dict[str, Any]:
    """Monta dict de resposta padronizado."""
    erro_normalizado = str(erro) if erro is not None else None
    
    return {
        "usina_nome": nome_usina,
        "usina_slug": slug_usina,
        "dispositivo_nome": nome_dispositivo,
        "potencia_ativa_mw": potencia_ativa_mw,
        "descricao": descricao,
        "tempo_leitura": tempo_leitura,
        "erro": erro_normalizado,
    }

