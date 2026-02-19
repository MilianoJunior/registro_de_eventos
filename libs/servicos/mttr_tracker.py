# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _descricao_indica_manutencao → verifica se a descrição indica manutenção
# 2. atualizar         → recebe payload da coleta e acumula MTTR em memória
# 3. get_mttr_atual    → retorna dict {slug: {mttr_str}} sem banco
# -------------------------------------------------------------------

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any, Dict, Optional

# -------------------------------------------------------------------
# ESTADO GLOBAL (thread-safe via Lock)
# -------------------------------------------------------------------
_lock = threading.Lock()

_estado: Dict[str, Dict[str, bool]] = {}        # slug → {dispositivo → em_manutencao}
_totais: Dict[str, Dict[str, float]] = {}        # slug → {tempo_manutencao, eventos}
_ultimo_ts: Optional[datetime] = None

# -------------------------------------------------------------------
# FUNÇÕES
# -------------------------------------------------------------------
def _descricao_indica_manutencao(descricao: str) -> bool:
    d = (descricao or "").lower()
    return "manutencao" in d or "manutenção" in d


def _formatar_mttr(tempo_min: float, eventos: float) -> str:
    mttr = (tempo_min / eventos) if eventos > 0 else tempo_min
    if mttr <= 0:
        return "0 min"
    h, m = int(mttr // 60), int(mttr % 60)
    return f"{h}h {m}m" if h > 0 else f"{m} min"


def atualizar(payload: Dict[str, Any]) -> None:
    """
    Recebe o payload bruto de cada coleta e acumula MTTR de manutenção
    por usina em memória. Thread-safe.
    """
    global _ultimo_ts

    ts_atual = datetime.now()

    with _lock:
        ts_ant = _ultimo_ts
        _ultimo_ts = ts_atual

        if ts_ant is None:
            return

        dt_min = (ts_atual - ts_ant).total_seconds() / 60.0
        if dt_min <= 0 or dt_min > 60.0:
            return

        for usina in payload.get("usinas") or []:
            slug = usina.get("slug")
            if not slug:
                continue

            _estado.setdefault(slug, {})
            _totais.setdefault(slug, {"tempo_manutencao": 0.0, "eventos": 0.0})

            dispositivos = usina.get("dispositivos") or {}
            if not isinstance(dispositivos, dict):
                continue

            for nome_disp, info in dispositivos.items():
                if not isinstance(info, dict):
                    continue

                em_manutencao = _descricao_indica_manutencao(info.get("descricao") or "")
                ultimo = _estado[slug].get(nome_disp, False)

                if em_manutencao:
                    _totais[slug]["tempo_manutencao"] += dt_min
                if em_manutencao and not ultimo:
                    _totais[slug]["eventos"] += 1.0

                _estado[slug][nome_disp] = em_manutencao


def get_mttr_atual() -> Dict[str, Dict[str, str]]:
    """Retorna MTTR acumulado por usina. Leitura em memória — 0ms."""
    with _lock:
        return {
            slug: {"mttr_str": _formatar_mttr(t["tempo_manutencao"], t["eventos"])}
            for slug, t in _totais.items()
        }


def resetar() -> None:
    """Reseta o acumulador (uso em testes ou reinício de janela diária)."""
    global _ultimo_ts
    with _lock:
        _estado.clear()
        _totais.clear()
        _ultimo_ts = None
