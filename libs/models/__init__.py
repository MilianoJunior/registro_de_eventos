"""
Módulo para configuração de filtros customizados do Jinja2.
Centraliza a configuração de filtros relacionados à apresentação de dados.
"""

from libs.models.filters import TEMPLATE_FILTERS


def register_template_filters(app):
    """
    Registra todos os filtros customizados no ambiente Jinja2 da aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    app.jinja_env.filters.update(TEMPLATE_FILTERS)
