"""Registradores de handlers Socket.IO."""

from .status_usina import _1_register_status_usina_handler
from .testar_leitura import register_testar_leitura_handler
from libs.controllers.decorador import desempenho


@desempenho
def register_socket_handlers(socketio):
    """Registra todos os handlers Socket.IO da aplicação."""
    register_testar_leitura_handler(socketio)
    _1_register_status_usina_handler(socketio)


__all__ = ["register_socket_handlers"]
