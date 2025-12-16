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
# -------------------------------------------------------------------

from flask import render_template, jsonify, Response, request
from main import app
from libs.controllers.homeController import HomeController
from libs.controllers.usinasController import UsinasController
# from libs.controllers.eventosController import EventosController
from libs.controllers.ocorrenciasController import OcorrenciasController
# from libs.controllers.analiseController import AnaliseController
from libs.controllers.configController import ConfigController
from libs.controllers.decorador import desempenho

from flask import render_template

homeController = HomeController()
usinasController = UsinasController()
ocorrenciasController = OcorrenciasController()
# analiseController = AnaliseController()
configController = ConfigController()

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("imgs/engegom.ico")

@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def chrome_devtools_probe():
    return Response(status=204)

@app.route("/")
@desempenho
def index():
    print('3- index')
    return homeController.home()

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

# @app.route("/analise-relatorios")
# def analise_relatorios():
#     print('7- analise_relatorios')
#     return analiseController.analise_relatorios()
