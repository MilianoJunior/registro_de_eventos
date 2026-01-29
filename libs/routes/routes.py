# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. index → renderiza o dashboard (home)
# 2. usina_page → renderiza página da usina
# 3. ocorrencias → renderiza página HTML de ocorrências
# 4. salvar_ocorrencia → API POST (JSON) para criar ocorrência
# 5. listar_ocorrencias → API GET (JSON) para listar ocorrências (filtros via querystring)
# 6. resolver_ocorrencia → API PUT/POST (JSON) para resolver ocorrência
# 7. configuracoes → renderiza página HTML de configurações
# 8. salvar_configuracao → persiste configurações (POST)
# 9. carregar_configuracao → carrega configurações (GET)
# 10. temperaturas_page → renderiza página HTML de temperaturas
# -------------------------------------------------------------------

from flask import render_template, jsonify, Response, request, send_from_directory, session, redirect, url_for
import os
import time
from main import app
from libs.controllers.homeController import HomeController
from libs.controllers.usinasController import UsinasController
# from libs.controllers.eventosController import EventosController
from libs.controllers.ocorrenciasController import OcorrenciasController
# from libs.controllers.analiseController import AnaliseController
from libs.controllers.configController import ConfigController
from libs.controllers.ratsController import RatsController
from libs.models.modelstate import DadosContexto
from libs.controllers.decorador import desempenho

# Usuários em memória (sem banco)
USERS = {
    'junior': {
        'password': 'Jun654123@',
        'name': 'Junior',
        'email': 'junior@engesep.com.br',
        'role': 'admin'
    },
    'gelson': {
        'password': 'Gel654123@',
        'name': 'Gelson',
        'email': 'gelson@engesep.com.br',
        'role': 'admin'
    },
    'leandro': {
        'password': 'Lea654123@',
        'name': 'Leandro',
        'email': 'leandro@engesep.com.br',
        'role': 'user'
    },
    'felipe': {
        'password': 'Fel654123@',
        'name': 'Felipe',
        'email': 'felipe@engesep.com.br',
        'role': 'user'
    },
    'gisele':{
        'password': 'Gis654123@',
        'name': 'Gisele',
        'email': 'gisele@engesep.com.br',
        'role': 'user'
    },
    'pedro':{
        'password': 'Ped654123@',
        'name': 'Pedro',
        'email': 'pedro@engesep.com.br',
        'role': 'user'
    },
    'laura':{
        'password': 'Lau654123@',
        'name': 'Laura',
        'email': 'laura@engesep.com.br',
        'role': 'user'
    },
    'user':{
        'password': 'Use654123@',
        'name': 'User',
        'email': 'user@engesep.com.br',
        'role': 'user'
    }
}
'''
Agora vamos criar a seguinte lógica de cadastramento,  quando alguém se conectar com o usuario user, esse usuario vai ser redirecionando para a pagina de cadastramento, 
sendo assim, onde constara apenas os campos de nome, email, senha, perfil e confirmar senha, e um botão para cadastrar o usuário.
'''
# Rate-limit simples em memória para login (5 tentativas / 5 min por IP)
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 300
_login_attempts = {}

def _get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    print(f"forwarded: {forwarded}")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"

def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    attempts = _login_attempts.get(ip, [])
    attempts = [ts for ts in attempts if now - ts <= LOGIN_WINDOW_SECONDS]
    _login_attempts[ip] = attempts
    return len(attempts) >= LOGIN_MAX_ATTEMPTS

def _register_failed_attempt(ip: str) -> None:
    now = time.time()
    attempts = _login_attempts.get(ip, [])
    attempts = [ts for ts in attempts if now - ts <= LOGIN_WINDOW_SECONDS]
    attempts.append(now)
    _login_attempts[ip] = attempts

homeController = HomeController()
usinasController = UsinasController()
ocorrenciasController = OcorrenciasController()
# analiseController = AnaliseController()
configController = ConfigController()
ratsController = RatsController()


def _autenticar(identifier: str, password: str):
    if not identifier or not password:
        return None
    ident = identifier.strip().lower()
    if ident in USERS and USERS[ident].get('password') == password:
        return {'username': ident, **USERS[ident]}
    for username, user in USERS.items():
        if user.get('email', '').lower() == ident and user.get('password') == password:
            return {'username': username, **user}
    return None

@app.before_request
def exigir_login():
    path = request.path or ""
    rotas_livres = (
        path.startswith("/login") or
        path.startswith("/static/") or
        path.startswith("/assets/") or
        path.startswith("/socket.io/") or
        path == "/favicon.ico" or
        path == "/.well-known/appspecific/com.chrome.devtools.json"
    )
    if rotas_livres:
        return None
    if session.get("usuario"):
        return None
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None, identifier="")

    client_ip = _get_client_ip()
    if _is_rate_limited(client_ip):
        return render_template(
            "login.html",
            error="Muitas tentativas. Tente novamente em alguns minutos.",
            identifier=request.form.get("identifier", ""),
        ), 429

    identifier = request.form.get("identifier", "")
    password = request.form.get("password", "")
    remember = request.form.get("remember")
    user = _autenticar(identifier, password)
    if not user:
        _register_failed_attempt(client_ip)
        return render_template(
            "login.html",
            error="Credenciais inválidas. Tente novamente.",
            identifier=identifier,
        ), 401

    session.permanent = bool(remember)
    session["usuario"] = {
        "username": user["username"],
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role"),
    }
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@desempenho
def index():
    print('3- index')
    return homeController.home()

@app.route("/monitoramento")
def monitoramento():
    return homeController.monitoramento()

@app.route("/usina/<sigla>")
# @desempenho
def usina_page(sigla):
    print('4- usina_page', sigla)
    # carregar métricas / ocorrências da usina
    return usinasController.usina_page(sigla)

@app.route("/ocorrencias")
# @desempenho
def ocorrencias():
    print('5- ocorrencias')
    return ocorrenciasController.ocorrencias_page()

@app.route("/salvar_ocorrencia", methods=["POST"])
# @desempenho
def salvar_ocorrencia():
    print('6- salvar_ocorrencia', request.method)
    return ocorrenciasController.criar_ocorrencia()

@app.route("/listar_ocorrencias", methods=["GET"])
# @desempenho
def listar_ocorrencias():
    print('6- listar_ocorrencias')
    return ocorrenciasController.listar_ocorrencias()

@app.route("/resolver_ocorrencia/<int:id>", methods=["PUT", "POST"])
# @desempenho
def resolver_ocorrencia(id):
    print('7- resolver_ocorrencia', id)
    return ocorrenciasController.resolver_ocorrencia(id)

@app.route("/configuracoes")
# @desempenho
def configuracoes():
    print('7- configuracoes')
    return configController.config_page()

@app.route("/configuracoes/salvar", methods=["POST"])
# @desempenho
def salvar_configuracao():
    print('8- salvar_configuracao')
    return configController.salvar_configuracao()

@app.route("/configuracoes/carregar", methods=["GET"])
# @desempenho
def carregar_configuracao():
    print('9- carregar_configuracao')
    return configController.carregar_configuracao()

@app.route("/temperaturas")
def temperaturas_page():
    ctx = DadosContexto()
    temperaturas = ctx.get_temperaturas()
    usinas = ctx.get_usinas()
    return render_template("temperaturas.html", temperaturas=temperaturas, usinas=usinas)

# @app.route("/analise-relatorios")
# def analise_relatorios():
#     print('7- analise_relatorios')
#     return analiseController.analise_relatorios()

@app.route('/rats')
def rats():
    return ratsController.inforat()

@app.route('/criarrat')
def criarrat():
    return ratsController.criarrat()

@app.route('/rat/salvar', methods=['POST'])
def salvar_rat():
    return ratsController.salvarrat()

@app.route('/rat/upload_foto', methods=['POST'])
def upload_foto():
    return ratsController.upload_foto()

@app.route('/rat/ver/<int:rat_id>', methods=['GET'])
def ver_rat(rat_id):
    return ratsController.ver_rat(rat_id)

@app.route('/modificarrat', defaults={'rat_id': None})
@app.route('/modificarrat/<int:rat_id>')
def modificarrat(rat_id):
    return ratsController.modificarrat(rat_id)

@app.route('/produtos/buscar', methods=['GET'])
def buscar_produtos():
    return ratsController.buscar_produtos()

@app.route('/rat/atualizar', methods=['POST'])
def atualizar_rat():
    return ratsController.atualizar_rat()

@app.route('/rat/atualizar_status_financeiro', methods=['POST'])
def atualizar_status_financeiro():
    return ratsController.atualizar_status_financeiro()

@app.route('/rat/deletar', methods=['POST'])
def deletar_rat():
    return ratsController.deletar_rat()

@app.route('/rat/pdf/<int:rat_id>', methods=['GET'])
def gerar_pdf(rat_id):
    return ratsController.gerar_pdf(rat_id)

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("imgs/engegom.ico")

@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def chrome_devtools_probe():
    return Response(status=204)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    # Serve files from the assets directory located at the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_folder = os.path.join(base_dir, 'assets')
    return send_from_directory(assets_folder, filename)