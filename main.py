from flask import Flask
from flask_socketio import SocketIO, emit
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import socket
import threading
import os
import time
from threading import Timer

# Configurar caminhos
template_dir = os.path.abspath('libs/views')
static_dir = os.path.abspath('libs/views/static')

# Criar app com configuração de templates
app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir,
           static_url_path='/static')

app.config['SECRET_KEY'] = 'secret!'

# Configurar filtros customizados para templates
from libs.models.utils import register_template_filters
register_template_filters(app)

# # Importa as rotas depois de criar a aplicação
from libs.routes.routes import *

# Inicializa o SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Classe para lidar com eventos de mudança de arquivo
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, socketio):
        self.socketio = socketio
        self.last_modified = {}
        self._timer = None
        self.cont = 0

    def on_modified(self, event):
        
        if event.src_path.endswith('.html') or event.src_path.endswith('.css') or event.src_path.endswith('.js'):
            if event.src_path in self.last_modified:
                if time.time() - self.last_modified[event.src_path] < 1:
                    return
            self.last_modified[event.src_path] = time.time()
        
        print(self.cont,f"Arquivo modificado: {event.src_path}")
        self.socketio.emit("file_changed", {"path": event.src_path})

# Função para iniciar o observador
def setup_file_watcher(socketio):
    handler = FileChangeHandler(socketio)
    observer = Observer()
    observer.schedule(handler, '.', recursive=True)
    observer.start()
    return observer

if __name__ == '__main__':
    observer = setup_file_watcher(socketio)
    try:
        socketio.run(app, host='127.0.0.1', port=5000, debug=True)
    finally:
        observer.stop()
        observer.join()
