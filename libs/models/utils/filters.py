from datetime import datetime
from typing import Any, Optional


def dt_filter(value: Any) -> str:
    """
    Filtro para formatação de datas no Jinja2.
    Converte datetime objects para string formatada no padrão brasileiro.
    """
    if value is None:
        return ""
    
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    
    # Se não for datetime, tenta converter para string
    return str(value)


def clip_filter(value: Any, length: int = 100) -> str:
    """
    Filtro para truncar texto no Jinja2.
    Corta o texto no tamanho especificado e adiciona '...' se necessário.
    """
    if value is None:
        return ""
    
    text = str(value)
    if len(text) <= length:
        return text
    
    return text[:length] + "..."


# Dicionário com todos os filtros customizados para templates
TEMPLATE_FILTERS = {
    'dt': dt_filter,
    'clip': clip_filter,
}
