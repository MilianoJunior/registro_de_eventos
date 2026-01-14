# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. CacheStore.get/set/delete/clear → cache global simples com TTL + prints (HIT/MISS/EXPIRED/SET/DEL)
# 2. _normalizar_cache_ocorrencias → normaliza cache em dict {itens, ultimo_id, ultimo_created_at, atualizado_em}
# 3. _montar_payload_ocorrencias → monta payload padronizado para persistir no cache
# 4. DadosContexto.get_usinas/get_usuarios → cache de horas (dados quase estáticos)
# 5. DadosContexto.get_ocorrencias_* → cache incremental por id (busca só delta)
# 6. DadosContexto.get_stats_status/get_kpis_mttr → cache de curto prazo (indicadores)
# -------------------------------------------------------------------

# libs/models/modelstate.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import time
import inspect
import os
from libs.models.read import OpUsina, OpOcorrencia, OpUsuario, OpParadas
from libs.models.utils.mock_data import (
    DEVELOPER_MODE, 
    get_mock_data, 
    get_usina_by_sigla, 
    get_ocorrencias_por_usina
)
from libs.models.utils.utils import normalizar_slug
from libs.controllers.decorador import desempenho

# ============================================================================
# HELPERS (cache)
# ============================================================================
def _normalizar_cache_ocorrencias(cached: Any) -> Dict[str, Any]:
    if isinstance(cached, dict):
        return cached
    if isinstance(cached, list):
        return {
            "itens": cached,
            "ultimo_id": (cached[0].get("id") if cached else None),
            "ultimo_created_at": (cached[0].get("created_at") if cached else None),
            "atualizado_em": 0.0,
        }
    return {"itens": [], "ultimo_id": None, "ultimo_created_at": None, "atualizado_em": 0.0}

def _montar_payload_ocorrencias(itens: List[Dict[str, Any]], now: float, cached: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if itens:
        return {
            "itens": itens,
            "ultimo_id": itens[0].get("id"),
            "ultimo_created_at": itens[0].get("created_at"),
            "atualizado_em": now,
        }
    return {
        "itens": [],
        "ultimo_id": (cached.get("ultimo_id") if cached else None),
        "ultimo_created_at": (cached.get("ultimo_created_at") if cached else None),
        "atualizado_em": now,
    }

def _parse_data_filtro(valor: str, fim_do_dia: bool) -> Optional[datetime]:
    if not valor:
        return None
    try:
        base = datetime.strptime(valor, "%Y-%m-%d")
    except Exception:
        return None
    if fim_do_dia:
        return base.replace(hour=23, minute=59, second=59, microsecond=999999)
    return base.replace(hour=0, minute=0, second=0, microsecond=0)

# ============================================================================
# CONFIGURAÇÕES / CONSTANTES (TTL)
# ============================================================================
TTL_USINAS_SEG = 6 * 60 * 60
TTL_USUARIOS_SEG = 6 * 60 * 60
TTL_USINA_SIGLA_SEG = 6 * 60 * 60
TTL_STATS_STATUS_SEG = 5 * 60
TTL_KPIS_MTTR_SEG = 5 * 60
TTL_OCORRENCIAS_SEG = 6 * 60 * 60
TTL_OCORRENCIAS_REQUER_ACAO_SEG = 30
REFRESH_OCORRENCIAS_SEG = 60
MAX_OCORRENCIAS_POR_USINA = 30
TTL_TEMPERATURAS_SEG = 60

# ============================================================================
# GERENCIADOR DE DADOS (Data Layer + Cache Global)
# ============================================================================
class CacheStore:
    """Armazém global de cache com expiração simples (TTL)"""
    _data = {}
    _expiry = {}
    
    @classmethod
    def get(cls, key: str):
        try:
            frame = inspect.stack()[1]
            origem = f"{os.path.basename(frame.filename)}:{frame.function}"
        except Exception:
            origem = "origem_desconhecida"

        if key not in cls._data:
            evento = "MISS"
            print(f"[CACHE] {evento} key={key!r} caller={origem}")
            return None

        if time.time() < cls._expiry.get(key, 0):
            evento = "HIT"
            print(f"[CACHE] {evento} key={key!r} caller={origem}")
            return cls._data[key]

        evento = "EXPIRED"
        print(f"[CACHE] {evento} key={key!r} caller={origem}")
        del cls._data[key]
        del cls._expiry[key]
        return None
    
    @classmethod
    def set(cls, key: str, value: Any, ttl_seconds: int = 60):
        try:
            frame = inspect.stack()[1]
            origem = f"{os.path.basename(frame.filename)}:{frame.function}"
        except Exception:
            origem = "origem_desconhecida"

        cls._data[key] = value
        cls._expiry[key] = time.time() + ttl_seconds
        evento = "SET"
        print(f"[CACHE] {evento} key={key!r} caller={origem}")
    
    @classmethod
    def clear(cls):
        try:
            frame = inspect.stack()[1]
            origem = f"{os.path.basename(frame.filename)}:{frame.function}"
        except Exception:
            origem = "origem_desconhecida"

        evento = "CLEAR"
        print(f"[CACHE] {evento} key={'*'!r} caller={origem}")
        cls._data = {}
        cls._expiry = {}

    @classmethod
    def delete_by_prefix(cls, prefix: str):
        keys_to_delete = [k for k in cls._data.keys() if k.startswith(prefix)]
        for k in keys_to_delete:
            del cls._data[k]
            if k in cls._expiry:
                del cls._expiry[k]
        print(f"[CACHE] DELETED_PREFIX prefix={prefix!r} count={len(keys_to_delete)}")

class DadosContexto:
    """
    Gerencia o acesso aos dados usando cache global.
    """
    def __init__(self):
        # Models de leitura
        self._op_usina = OpUsina()
        self._op_ocorrencia = OpOcorrencia()
        self._op_parada = OpParadas()
        self._op_usuario = OpUsuario()
        self.developer_mode = DEVELOPER_MODE

    def invalidar_cache_ocorrencias(self):
        """Limpa todo cache relacionado a ocorrências e status"""
        CacheStore.delete_by_prefix('ocorrencias_')
        CacheStore.delete_by_prefix('stats_status')
        print("[CACHE] Cache de ocorrências invalidado")

    @desempenho
    def get_usinas(self) -> List[Dict]:
        if self.developer_mode:
            return get_mock_data('op_usina') or []
            
        # Cache de horas: cadastro de usinas muda pouco
        cached = CacheStore.get('usinas')
        if cached is not None:
            return cached
            
        data = self._op_usina.all()
        CacheStore.set('usinas', data, ttl_seconds=TTL_USINAS_SEG)
        return data

    @desempenho
    def get_usina_por_sigla(self, sigla: str) -> Optional[Dict]:
        if self.developer_mode:
            return get_usina_by_sigla(sigla)
            
        # Não cachear usina individual por enquanto ou usar chave composta
        key = f'usina_{sigla}'
        cached = CacheStore.get(key)
        if cached is not None:
            return cached
            
        data = self._op_usina.first({"sigla": sigla})
        if data:
            CacheStore.set(key, data, ttl_seconds=TTL_USINA_SIGLA_SEG)
        return data

    @desempenho
    def get_usuarios(self) -> List[Dict]:
        if self.developer_mode:
            return get_mock_data('op_usuario') or []

        cached = CacheStore.get('usuarios')
        if cached is not None:
            return cached

        data = self._op_usuario.all()
        CacheStore.set('usuarios', data, ttl_seconds=TTL_USUARIOS_SEG)
        return data

    @desempenho
    def get_ocorrencias_recentes(self, limit=20) -> List[Dict]:
        if self.developer_mode:
            return [] 
        
        # Cache incremental por created_at (evita reconsultar tudo)
        key = f'ocorrencias_{limit}'
        cached = CacheStore.get(key)
        now = time.time()

        if cached is None:
            itens = self._op_ocorrencia.listar_recentes_por_id(limit=limit)
            payload = _montar_payload_ocorrencias(itens, now)
            CacheStore.set(key, payload, ttl_seconds=TTL_OCORRENCIAS_SEG)
            return itens

        cached = _normalizar_cache_ocorrencias(cached)

        if (now - float(cached.get("atualizado_em") or 0)) < REFRESH_OCORRENCIAS_SEG:
            return cached.get("itens") or []

        ultimo_id = cached.get("ultimo_id")
        novos = []
        if ultimo_id:
            novos = self._op_ocorrencia.listar_novas_por_id(ultimo_id=int(ultimo_id), limit=200)

        merged = (novos or []) + (cached.get("itens") or [])
        seen = set()
        out = []
        for item in merged:
            _id = item.get("id")
            if _id in seen:
                continue
            seen.add(_id)
            out.append(item)
            if len(out) >= int(limit):
                break

        payload = _montar_payload_ocorrencias(out, now, cached=cached)
        CacheStore.set(key, payload, ttl_seconds=TTL_OCORRENCIAS_SEG)
        return out

    @desempenho
    def get_ocorrencias_usina(
        self,
        usina_id: int,
        limit: int = 50,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
    ) -> List[Dict]:
        if self.developer_mode:
             return get_ocorrencias_por_usina(usina_id, limit=limit)
             
        limit = min(int(limit or MAX_OCORRENCIAS_POR_USINA), MAX_OCORRENCIAS_POR_USINA)
        periodo_key = ""
        if data_inicio or data_fim:
            di = data_inicio.strftime("%Y-%m-%d") if data_inicio else ""
            df = data_fim.strftime("%Y-%m-%d") if data_fim else ""
            periodo_key = f"_{di}_{df}"

        key = f'ocorrencias_usina_{usina_id}_{limit}{periodo_key}'
        cached = CacheStore.get(key)
        now = time.time()

        if cached is None:
            if data_inicio or data_fim:
                itens = self._op_ocorrencia.listar_usina_por_periodo(usina_id=usina_id, data_inicio=data_inicio, data_fim=data_fim, limit=limit)
            else:
                itens = self._op_ocorrencia.listar_recentes_usina_por_id(usina_id=usina_id, limit=limit)
            payload = _montar_payload_ocorrencias(itens, now)
            CacheStore.set(key, payload, ttl_seconds=TTL_OCORRENCIAS_SEG)
            return itens

        cached = _normalizar_cache_ocorrencias(cached)

        if data_inicio or data_fim:
            return cached.get("itens") or []

        if (now - float(cached.get("atualizado_em") or 0)) < REFRESH_OCORRENCIAS_SEG:
            return cached.get("itens") or []

        ultimo_id = cached.get("ultimo_id")
        novos = []
        if ultimo_id:
            novos = self._op_ocorrencia.listar_novas_usina_por_id(usina_id=usina_id, ultimo_id=int(ultimo_id), limit=200)

        merged = (novos or []) + (cached.get("itens") or [])
        seen = set()
        out = []
        for item in merged:
            _id = item.get("id")
            if _id in seen:
                continue
            seen.add(_id)
            out.append(item)
            if len(out) >= int(limit):
                break

        payload = _montar_payload_ocorrencias(out, now, cached=cached)
        CacheStore.set(key, payload, ttl_seconds=TTL_OCORRENCIAS_SEG)
        return out

    @desempenho
    def get_stats_status(self) -> Dict[str, int]:
        """Busca contagem real de status no banco"""
        if self.developer_mode: return {}
        
        cached = CacheStore.get('stats_status')
        if cached is not None:
            return cached
        
        # Usa o método otimizado do Read
        data = self._op_ocorrencia.get_counts_by_status()
        CacheStore.set('stats_status', data, ttl_seconds=TTL_STATS_STATUS_SEG)
        return data

    @desempenho
    def get_kpis_mttr(self) -> Dict:

        cached = CacheStore.get('kpis_mttr')
        if cached is not None:
            return cached

        data = self._op_parada.get_indicadores_manutencao(periodo='diario')
        CacheStore.set('kpis_mttr', data, ttl_seconds=TTL_KPIS_MTTR_SEG)
        return data

    @desempenho
    def get_ocorrencias_requer_acao(self) -> List[Dict]:
        if self.developer_mode:
            return []
        
        cached = CacheStore.get('ocorrencias_requer_acao')
        if cached is not None:
            return cached
        
        data = self._op_ocorrencia.listar_requer_acao()
        CacheStore.set('ocorrencias_requer_acao', data, ttl_seconds=TTL_OCORRENCIAS_REQUER_ACAO_SEG)
        return data

    @desempenho
    def get_temperaturas(self) -> List[Dict]:
        if self.developer_mode:
            return []
        
        cached = CacheStore.get('temperaturas')
        if cached is not None:
            return cached
        
        data = self._op_parada.get_temperaturas()
        CacheStore.set('temperaturas', data, ttl_seconds=TTL_TEMPERATURAS_SEG)
        return data

# ============================================================================
# MODELOS DE APRESENTAÇÃO (ViewModels)
# ============================================================================
@dataclass
class KpiUsina:
    """Card de Usina na Home"""
    nome: str
    sigla: str
    mttr: str
    status_operacional: str = "Carregando..."
    status_classe_css: str = "bg-gray-400"
    potencia_mw: float = 0.0
    alarmes_por_hora: float = 0.0
    alarmes_criticos: int = 0
    id: int = 0
    
    @classmethod
    @desempenho
    def from_dict(cls, dado: Dict, mttr_info: Dict = None) -> 'KpiUsina':
        nome = dado.get('nome', 'N/A')
        mttr_str = mttr_info.get('mttr_str', '0 min') if mttr_info else '0 min'
        print(f"               KpiUsina.from_dict - nome: {nome}, mttr_str: {mttr_str}")
        return cls(
            id=dado.get('id', 0),
            nome=nome,
            sigla=dado.get('sigla', nome[:4].upper()),
            mttr=mttr_str
        )

@dataclass
class HomePageViewModel:
    usinas: List[KpiUsina]
    ocorrencias_recentes: List[Dict]
    stats_por_status: Dict[str, int]
    potencia_total_mw: Any = "__"
    temperaturas: List[Dict] = field(default_factory=list)

    @classmethod
    @desempenho
    def carregar(cls, ctx: DadosContexto) -> 'HomePageViewModel':
        raw_usinas = ctx.get_usinas()
        raw_ocorrencias = ctx.get_ocorrencias_recentes(limit=15)
        kpis_mttr = ctx.get_kpis_mttr()
        real_stats = ctx.get_stats_status()
        temperaturas = ctx.get_temperaturas()

        usinas_objs = []
        for u in raw_usinas:
            slug = normalizar_slug(u.get('nome', ''))
            mttr_data = kpis_mttr.get(slug)
            usinas_objs.append(KpiUsina.from_dict(u, mttr_data))

        return cls(
            usinas=usinas_objs,
            ocorrencias_recentes=raw_ocorrencias,
            stats_por_status=real_stats,
            potencia_total_mw="__",
            temperaturas=temperaturas
        )

@dataclass
class OcorrenciasPageViewModel:
    usinas: List[Dict]
    usuarios: List[Dict]
    ocorrencias_requer_acao: List[Dict]
    templates: List[Dict]
    categorias: List[str]
    tipos: List[str]

    @classmethod
    @desempenho
    def carregar(cls, ctx: DadosContexto) -> 'OcorrenciasPageViewModel':
        usinas = ctx.get_usinas()
        usuarios = ctx.get_usuarios()
        ocorrencias_requer_acao = ctx.get_ocorrencias_requer_acao()
        for ocorrencia in ocorrencias_requer_acao:
            print(f"ocorrencia: {ocorrencia}")
            print('-' * 50)

        templates = [
            {"id": "manutencao_preventiva", "nome": "Manutenção Preventiva", "texto": "Realizada manutenção preventiva conforme plano estabelecido..."},
            {"id": "parada_emergencia", "nome": "Parada de Emergência", "texto": "Acionada parada de emergência devido a detecção de anomalia..."},
            {"id": "trip_geracao", "nome": "Trip de Geração", "texto": "Unidade geradora desligada automaticamente..."},
            {"id": "falha_equipamento", "nome": "Falha de Equipamento", "texto": "Identificada falha no equipamento..."},
            {"id": "oscilacao_tensao", "nome": "Oscilação de Tensão", "texto": "Registrada oscilação de tensão fora dos parâmetros normais..."}
        ]
        
        categorias = ["Operação/Humano", "Elétrica", "Hidráulica", "Mecânica", "Automação", "Segurança", "Ambiental"]
        tipos = ["Evento", "Alarme", "Trip", "Comando", "Manutenção"]

        return cls(
            usinas=usinas,
            usuarios=usuarios,
            templates=templates,
            categorias=categorias,
            tipos=tipos,
            ocorrencias_requer_acao=ocorrencias_requer_acao,
        )

@dataclass
class ConfiguracoesPageViewModel:
    usinas: List[Dict]

    @classmethod
    @desempenho
    def carregar(cls, ctx: DadosContexto) -> 'ConfiguracoesPageViewModel':
        usinas = ctx.get_usinas()
        return cls(usinas=usinas)

@dataclass
class UsinasPageViewModel:
    usina: Optional[Dict]
    usinas: List[Dict]
    timeline_filtrada: List[Dict]
    sigla: str
    data_inicio: str = ""
    data_fim: str = ""

    @classmethod
    @desempenho
    def carregar(cls, ctx: DadosContexto, sigla: str, data_inicio: str = "", data_fim: str = "", limit: int = 30) -> 'UsinasPageViewModel':
        usinas = ctx.get_usinas()
        usina = ctx.get_usina_por_sigla(sigla)
        kpis_mttr = ctx.get_kpis_mttr()
        
        timeline_filtrada = []
        if usina:
            dt_inicio = _parse_data_filtro(data_inicio, fim_do_dia=False)
            dt_fim = _parse_data_filtro(data_fim, fim_do_dia=True)
            raw_timeline = ctx.get_ocorrencias_usina(usina['id'], limit=limit, data_inicio=dt_inicio, data_fim=dt_fim)
            
            for ocorrencia in raw_timeline:
                meta = ocorrencia.get('metadata')
                if meta and isinstance(meta, str):
                    try:
                        ocorrencia['metadata'] = json.loads(meta)
                    except (json.JSONDecodeError, TypeError):
                        ocorrencia['metadata'] = {}
                elif not meta:
                    ocorrencia['metadata'] = {}
                timeline_filtrada.append(ocorrencia)

            slug = normalizar_slug(usina.get('nome', ''))
            mttr_info = kpis_mttr.get(slug, {})
            usina['mttr'] = mttr_info.get('mttr_str', '0 min')

            # Adiciona campos placeholder/mock se não existirem (simulando dados reais que virão de outra fonte ou socket)
            if 'status_operacional' not in usina: usina['status_operacional'] = 'operando'
            if 'potencia_ativa_mw' not in usina: usina['potencia_ativa_mw'] = 1200
            if 'alarmes_por_hora' not in usina: usina['alarmes_por_hora'] = 8.0
            if 'alarmes_criticos' not in usina: usina['alarmes_criticos'] = 0
            if 'incidentes_abertos' not in usina: usina['incidentes_abertos'] = 0
            if 'alarmes_atencao' not in usina: usina['alarmes_atencao'] = 3
            if 'alarmes_inundantes' not in usina: usina['alarmes_inundantes'] = 0
            if 'alarmes_oscilantes' not in usina: usina['alarmes_oscilantes'] = 2
            if 'energia_nao_gerada_mwh' not in usina: usina['energia_nao_gerada_mwh'] = 0
            if 'distribuicao_prioridade' not in usina: 
                usina['distribuicao_prioridade'] = {'alta': 0, 'media': 100, 'baixa': 0}

        return cls(
            usina=usina,
            usinas=usinas,
            timeline_filtrada=timeline_filtrada,
            sigla=sigla,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )