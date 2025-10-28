"""Registradores de handlers Socket.IO."""

from .testar_leitura import register_testar_leitura_handler


def register_socket_handlers(socketio):
    """Registra todos os handlers Socket.IO da aplicação."""
    register_testar_leitura_handler(socketio)


__all__ = ["register_socket_handlers"]
