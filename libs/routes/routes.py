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

@app.route("/api/ocorrencias", methods=["GET", "POST"])
# @desempenho
def api_ocorrencias():
    print('6- api_ocorrencias', request.method)
    if request.method == 'POST':
        return ocorrenciasController.criar_ocorrencia()
    return ocorrenciasController.get_ocorrencias()

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
