import re
import unicodedata
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


def slugify_filter(value: Any) -> str:
    """
    Filtro para gerar chaves normalizadas (slug) removendo acentos e caracteres especiais.
    Útil para atributos data-* em templates.
    """
    if value is None:
        return ""

    text = str(value)
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    # manter apenas letras e números
    return re.sub(r"[^a-z0-9]", "", without_accents.lower())


# Dicionário com todos os filtros customizados para templates
TEMPLATE_FILTERS = {
    'dt': dt_filter,
    'clip': clip_filter,
    'slugify': slugify_filter,
}
