
import os
import time
from flask import Flask
from flask_socketio import SocketIO, emit

# caminhos robustos (independe do diretório onde o service inicia)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'libs', 'views')
static_dir   = os.path.join(BASE_DIR, 'libs', 'views', 'static')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path='/static'
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

# filtros/rotas
from libs.models.utils import register_template_filters
register_template_filters(app)
from libs.routes.routes import *  # noqa

# dev: threading; prod: gunicorn -k eventlet (não precisa mudar aqui)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# --- Socket.IO event handlers ---
from libs.controllers.configController import ConfigController
from libs.models.readRT import get_data
import asyncio

@socketio.on('testar_leitura')
def handle_testar_leitura(payload):
    """Handler para testar leitura de variável do CLP"""
    config = payload.get('config', {})
    data = payload.get('data', {})
    entrada_id = payload.get('entrada_id')
    
    print(f"🧪 Recebido pedido de teste:")
    print(f"   Unidade: {config.get('unidade')}")
    print(f"   Tipo: {config.get('tipo')}")
    
    try:
        # Executar função async em thread separada
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resultado, tempo = loop.run_until_complete(get_data(config, data))
        loop.close()
        
        print(f"📊 Resultado da API: {resultado}")
        
        # Extrair o valor da resposta
        tipo_secao = config.get('tipo')  # leituras, temperaturas, etc
        
        if resultado:
            # Navegar pela estrutura de resposta para pegar o valor
            for tipo_dado, valores in resultado.items():  # REAL, INT, BOOLEAN
                for nome_var, valor in valores.items():
                    # Emitir sucesso
                    emit('resultado_teste_leitura', {
                        'entrada_id': entrada_id,
                        'status': 'success',
                        'nome': nome_var,
                        'tipo': tipo_dado,
                        'valor': valor,
                        'tempo': f"{tempo:.3f}s",
                        'message': 'Leitura realizada com sucesso'
                    })
                    return
        
        # Se não encontrou valor
        emit('resultado_teste_leitura', {
            'entrada_id': entrada_id,
            'status': 'error',
            'nome': 'desconhecida',
            'message': 'Nenhum valor retornado pela API'
        })
        
    except Exception as e:
        print(f"❌ Erro ao testar leitura: {e}")
        import traceback
        traceback.print_exc()
        emit('resultado_teste_leitura', {
            'entrada_id': entrada_id,
            'status': 'error',
            'nome': 'desconhecida',
            'message': f'Erro: {str(e)}'
        })

# --- watcher só em DEV ---
DEV_RELOAD = os.getenv("DEV_RELOAD", "0") == "1"
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

    def setup_file_watcher(socketio):
        handler = FileChangeHandler(socketio)
        observer = Observer()
        observer.schedule(handler, BASE_DIR, recursive=True)
        observer.start()
        return observer
# --- fim watcher ---

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

# from flask import Flask
# from flask_socketio import SocketIO, emit
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# import socket
# import threading
# import os
# import time
# from threading import Timer

# # Configurar caminhos
# template_dir = os.path.abspath('libs/views')
# static_dir = os.path.abspath('libs/views/static')

# # Criar app com configuração de templates
# app = Flask(__name__, 
#            template_folder=template_dir,
#            static_folder=static_dir,
#            static_url_path='/static')

# app.config['SECRET_KEY'] = 'secret!'

# # Configurar filtros customizados para templates
# from libs.models.utils import register_template_filters
# register_template_filters(app)

# # # Importa as rotas depois de criar a aplicação
# from libs.routes.routes import *

# # Inicializa o SocketIO
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# # Classe para lidar com eventos de mudança de arquivo
# class FileChangeHandler(FileSystemEventHandler):
#     def __init__(self, socketio):
#         self.socketio = socketio
#         self.last_modified = {}
#         self._timer = None
#         self.cont = 0

#     def on_modified(self, event):
        
#         if event.src_path.endswith('.html') or event.src_path.endswith('.css') or event.src_path.endswith('.js'):
#             if event.src_path in self.last_modified:
#                 if time.time() - self.last_modified[event.src_path] < 1:
#                     return
#             self.last_modified[event.src_path] = time.time()
        
#         print(self.cont,f"Arquivo modificado: {event.src_path}")
#         self.socketio.emit("file_changed", {"path": event.src_path})

# # Função para iniciar o observador
# def setup_file_watcher(socketio):
#     handler = FileChangeHandler(socketio)
#     observer = Observer()
#     observer.schedule(handler, '.', recursive=True)
#     observer.start()
#     return observer

# if __name__ == '__main__':
#     observer = setup_file_watcher(socketio)
#     try:
#         socketio.run(app, host='0.0.0.0', port=5000, debug=True)
#     finally:
#         observer.stop()
#         observer.join()
