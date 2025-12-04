# libs/models/modelstate.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
from libs.models.read import OpUsina, OpOcorrencia, OpUsuario, OpParadas
from libs.models.utils.mock_data import DEVELOPER_MODE, get_mock_data

# ============================================================================
# GERENCIADOR DE DADOS (Data Layer + Cache Global)
# ============================================================================
class CacheStore:
    """Armazém global de cache com expiração simples (TTL)"""
    _data = {}
    _expiry = {}
    
    @classmethod
    def get(cls, key: str):
        if key in cls._data:
            if time.time() < cls._expiry.get(key, 0):
                return cls._data[key]
            else:
                # Expirou
                del cls._data[key]
                del cls._expiry[key]
        return None
    
    @classmethod
    def set(cls, key: str, value: Any, ttl_seconds: int = 60):
        cls._data[key] = value
        cls._expiry[key] = time.time() + ttl_seconds
    
    @classmethod
    def clear(cls):
        cls._data = {}
        cls._expiry = {}

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

    def get_usinas(self) -> List[Dict]:
        if self.developer_mode:
            return get_mock_data('op_usina') or []
            
        # Tenta pegar do cache global (TTL 5 minutos para lista de usinas - muda pouco)
        cached = CacheStore.get('usinas')
        if cached is not None:
            return cached
            
        data = self._op_usina.get_all()
        CacheStore.set('usinas', data, ttl_seconds=300) 
        return data

    def get_usuarios(self) -> List[Dict]:
        if self.developer_mode:
            return get_mock_data('op_usuario') or []

        cached = CacheStore.get('usuarios')
        if cached is not None:
            return cached

        data = self._op_usuario.get_all()
        CacheStore.set('usuarios', data, ttl_seconds=300)
        return data

    def get_ocorrencias_recentes(self, limit=20) -> List[Dict]:
        if self.developer_mode:
            return [] 
        
        # Busca ocorrências gerais para a lista recente
        key = f'ocorrencias_{limit}'
        cached = CacheStore.get(key)
        if cached is not None:
            return cached

        data = self._op_ocorrencia.get_all(limit=limit)
        CacheStore.set(key, data, ttl_seconds=10)
        return data

    def get_stats_status(self) -> Dict[str, int]:
        """Busca contagem real de status no banco"""
        if self.developer_mode: return {}
        
        cached = CacheStore.get('stats_status')
        if cached: return cached
        
        # Usa o método otimizado do Read
        data = self._op_ocorrencia.get_counts_by_status()
        CacheStore.set('stats_status', data, ttl_seconds=60)
        return data

    def get_kpis_mttr(self) -> Dict:

        if self.developer_mode:
            return {}

        # Cálculo pesado! Cache longo (5 min)
        # Idealmente isso rodaria em background e salvaria em tabela de estatísticas,
        # mas o cache aqui já resolve o gargalo de carregamento da página.
        cached = CacheStore.get('kpis_mttr')
        if cached is not None:
            return cached

        data = self._op_parada.get_indicadores_manutencao(periodo='diario')
        CacheStore.set('kpis_mttr', data, ttl_seconds=300)
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
    # Placeholder para futuros status reais via socket
    status_operacional: str = "Carregando..."
    status_classe_css: str = "bg-gray-400"
    potencia_mw: float = 0.0
    alarmes_por_hora: float = 0.0
    alarmes_criticos: int = 0
    id: int = 0
    
    @classmethod
    def from_dict(cls, dado: Dict, mttr_info: Dict = None) -> 'KpiUsina':
        nome = dado.get('nome', 'N/A')
        mttr_str = mttr_info.get('mttr_str', '0 min') if mttr_info else '0 min'
        
        return cls(
            id=dado.get('id', 0),
            nome=nome,
            sigla=dado.get('sigla', nome[:4].upper()),
            mttr=mttr_str
        )

@dataclass
class Ocorrencias:
    """Linha de tabela de ocorrência"""
    id: int
    usina_id: int
    operador_id: int
    tipo: str
    categoria: str
    unidade: str
    tags: str
    playbook: str
    template_texto: str
    descricao: str
    status: str
    severidade: str
    origem: str
    metadata: dict
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime
    requer_acao: bool
    data_ocorrencia: datetime
    resolvida_por: str
    resolucao_descricao: str


    @classmethod
    def from_dict(cls, dado: Dict) -> 'Ocorrencias':
        # DEBUG: Imprimir dados brutos do banco
        print("=" * 60)
        print("DEBUG Ocorrencias.from_dict - Dados recebidos:")
        for k, v in dado.items():
            print(f"  {k}: {repr(v)[:80]}")
        print("=" * 60)
        
        return cls(
            id=dado.get('id'),
            usina_id=dado.get('usina_id'),
            operador_id=dado.get('operador_id'),
            tipo=dado.get('tipo', ''),
            categoria=dado.get('categoria', ''),
            unidade=dado.get('unidade', ''),
            tags=dado.get('tags', ''),
            playbook=dado.get('playbook', ''),
            template_texto=dado.get('template_texto', ''),
            descricao=dado.get('descricao', ''),
            status=dado.get('status', 'aberta'),
            severidade=dado.get('severidade', 'média'),
            origem=dado.get('origem', 'humano'),
            metadata=dado.get('metadata') or {},
            created_at=dado.get('created_at'),
            updated_at=dado.get('updated_at'),
            resolved_at=dado.get('resolved_at'),
            requer_acao=dado.get('requer_acao', False),
            data_ocorrencia=dado.get('data_ocorrencia'),
            resolvida_por=dado.get('resolvida_por'),
            resolucao_descricao=dado.get('resolucao_descricao', '')
        )

@dataclass
class HomePageViewModel:
    """
    Estado completo da Home.
    """
    usinas: List[KpiUsina]
    ocorrencias_recentes: List[Ocorrencias]
    stats_por_status: Dict[str, int]
    stats_por_unidade: List[tuple]
    total_ocorrencias: int
    potencia_total_mw: float = 0.0

    @classmethod
    def carregar(cls, ctx: DadosContexto) -> 'HomePageViewModel':
        raw_usinas = ctx.get_usinas()
        raw_ocorrencias = ctx.get_ocorrencias_recentes(limit=20)
        kpis_mttr = ctx.get_kpis_mttr()
        real_stats = ctx.get_stats_status()

        usinas_objs = []
        for u in raw_usinas:
            slug = _normalizar_slug(u.get('nome', ''))
            mttr_data = kpis_mttr.get(slug)
            usinas_objs.append(KpiUsina.from_dict(u, mttr_data))

        ocorrencias_objs = [Ocorrencias.from_dict(o) for o in raw_ocorrencias]

        # Contagem de unidades baseada apenas nas recentes (ou implementar lógica global se necessário)
        from collections import Counter
        c_unidade = Counter(o.get('unidade', '-') for o in raw_ocorrencias)

        return cls(
            usinas=usinas_objs,
            ocorrencias_recentes=ocorrencias_objs[:10],
            stats_por_status=real_stats, # Usa a estatística real do banco
            stats_por_unidade=c_unidade.most_common(5),
            total_ocorrencias=sum(real_stats.values()) # Total baseado na soma dos status
        )

@dataclass
class OcorrenciasPageViewModel:
    """
    Estado completo da Página de Ocorrências.
    """
    usinas: List[Dict]
    usuarios: List[Dict]
    templates: List[Dict]
    categorias: List[str]
    tipos: List[str]

    @classmethod
    def carregar(cls, ctx: DadosContexto) -> 'OcorrenciasPageViewModel':
        # Reutiliza cache de usinas (e usuários se já tiver buscado)
        usinas = ctx.get_usinas()
        usuarios = ctx.get_usuarios()

        # Dados estáticos (podem vir do banco no futuro)
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
            tipos=tipos
        )

# ============================================================================
# UTILS
# ============================================================================
def _normalizar_slug(texto):
    import unicodedata, re
    if not texto: return ""
    n = unicodedata.normalize("NFKD", texto)
    s = "".join(c for c in n if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())
