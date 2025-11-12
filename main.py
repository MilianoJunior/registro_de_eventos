# --------------------------------------------------------------------------------
# imports librairies
# --------------------------------------------------------------------------------

import os
import time
from flask import Flask
from flask_socketio import SocketIO
from libs.controllers.decorador import desempenho
from libs.models.utils import register_template_filters

from libs.sockets import register_socket_handlers

# ----------------------------------------------------------------------------------
# caminhos robustos (independe do diretório onde o service inicia)
# ----------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'libs', 'views')
static_dir   = os.path.join(BASE_DIR, 'libs', 'views', 'static')
DEV_RELOAD = os.getenv("DEV_RELOAD", "0") == "1"

# ----------------------------------------------------------------------------------
# configuração do app Flask
# ----------------------------------------------------------------------------------

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path='/static'
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

# ----------------------------------------------------------------------------------
# filtros/rotas e configuração do Socket.IO
# ----------------------------------------------------------------------------------
from libs.routes.routes import *  # noqa

register_template_filters(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
register_socket_handlers(socketio)

# ---------------------------------------------------------------------------------
# watcher para recarregar arquivos estáticos em desenvolvimento
# ---------------------------------------------------------------------------------

if DEV_RELOAD:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class FileChangeHandler(FileSystemEventHandler):
        def __init__(self, socketio):
            self.socketio = socketio
            self.last_modified = {}

        def on_modified(self, event):
            if event.is_directory:
                return
            if event.src_path.endswith(('.html', '.css', '.js')):
                if event.src_path in self.last_modified and time.time() - self.last_modified[event.src_path] < 1:
                    return
                self.last_modified[event.src_path] = time.time()
                print(f"Arquivo modificado: {event.src_path}")
                self.socketio.emit("file_changed", {"path": event.src_path})

    @desempenho
    def setup_file_watcher(socketio):
        handler = FileChangeHandler(socketio)
        observer = Observer()
        observer.schedule(handler, BASE_DIR, recursive=True)
        observer.start()
        return observer
    
# ----------------------------------------------------------------------------------
# inicialização do servidor
# ----------------------------------------------------------------------------------

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5001"))
    observer = None
    try:
        if DEV_RELOAD:
            observer = setup_file_watcher(socketio)
        print(f'Iniciando servidor em 0.0.0.0:{port} (DEV_RELOAD={DEV_RELOAD})')
        socketio.run(app, host='0.0.0.0', port=port, debug=DEV_RELOAD)
    finally:
        if observer:
            observer.stop()
            observer.join()
