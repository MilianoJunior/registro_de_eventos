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

# # ----------------------------------------------------------------------------------
# # error handlers (captura 500 e exceções gerais)
# # ----------------------------------------------------------------------------------
# @app.errorhandler(500)
# def internal_server_error(e):
#     # Renderiza a página de erro amigável para erros internos
#     return render_template("error.html", error_code=500, error_msg=str(e)), 500

# @app.errorhandler(Exception)
# def handle_exception(e):
#     # Captura outras exceções não tratadas
#     import traceback
#     trace = traceback.format_exc()
#     print(f"[ERROR] Exceção não tratada: {e}\n{trace}")
#     return render_template("error.html", error_code=500, error_msg="Erro interno inesperado", debug_trace=trace if DEV_RELOAD else None), 500

# ----------------------------------------------------------------------------------
# filtros/rotas e configuração do Socket.IO
# ----------------------------------------------------------------------------------
from libs.routes.routes import *
from libs.servicos.coletor_core import coletar_status_completo
from libs.models.create import OpParadasCreate
import threading
import json

register_template_filters(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
register_socket_handlers(socketio)

# ---------------------------------------------------------------------------------
# thread background para coleta contínua de dados
# ---------------------------------------------------------------------------------

def coletor_background_thread():
    """
    Thread daemon que coleta dados das usinas a cada 30 segundos.
    Salva no banco e emite via Socket.IO (se houver clientes conectados).
    """
    print("[THREAD] Coletor background iniciado")
    intervalo_coleta = int(os.getenv("INTERVALO_COLETA", "30"))  # segundos
    
    while True:
        try:
            print(f"[THREAD] Iniciando coleta automática...")
            inicio = time.time()
            
            # Coleta dados (usa cache compartilhado com socket)
            payload = coletar_status_completo()
            
            # Salva no banco
            try:
                repo = OpParadasCreate()
                repo.insert({"dados": json.dumps(payload)})
                print(f"[THREAD] ✅ Snapshot salvo em op_paradas")
            except Exception as e:
                print(f"[THREAD] ❌ Erro ao salvar: {e}")
            
            # Emite para clientes conectados (se houver)
            try:
                socketio.emit("status_usinas_dados", payload, broadcast=True)
                print(f"[THREAD] ✅ Dados emitidos via Socket.IO")
            except Exception as e:
                print(f"[THREAD] ⚠️  Erro ao emitir (sem clientes?): {e}")
            
            duracao = time.time() - inicio
            print(f"[THREAD] Coleta finalizada em {duracao:.2f}s")
            
        except Exception as e:
            print(f"[THREAD] ❌ Erro na coleta: {e}")
        
        # Aguarda próximo ciclo
        time.sleep(intervalo_coleta)

# ---------------------------------------------------------------------------------
# watcher para recarregar arquivos estáticos em desenvolvimento
# ---------------------------------------------------------------------------------

if DEV_RELOAD:
    print('DEV_RELOAD is enabled')
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
else:
    print('DEV_RELOAD is not enabled')
    
# ----------------------------------------------------------------------------------
# inicialização do servidor
# ----------------------------------------------------------------------------------

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5001"))
    observer = None
    coletor_thread = None
    
    try:
        # Inicia file watcher (dev)
        if DEV_RELOAD:
            observer = setup_file_watcher(socketio)
        
        # Inicia thread de coleta background
        coletor_thread = threading.Thread(target=coletor_background_thread, daemon=True)
        coletor_thread.start()
        print(f'[MAIN] Thread de coleta iniciada (intervalo: {os.getenv("INTERVALO_COLETA", "30")}s)')
        
        print(f'[MAIN] Iniciando servidor em 0.0.0.0:{port} (DEV_RELOAD={DEV_RELOAD})')
        socketio.run(app, host='0.0.0.0', port=port, debug=DEV_RELOAD)
    finally:
        if observer:
            observer.stop()
            observer.join()
        print("[MAIN] Servidor encerrado")
