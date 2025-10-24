from flask import render_template, jsonify, Response, request
from main import app
from libs.controllers.homeController import HomeController
from libs.controllers.usinasController import UsinasController
from libs.controllers.eventosController import EventosController
# from libs.controllers.analiseController import AnaliseController
from libs.controllers.configController import ConfigController

from flask import render_template

homeController = HomeController()
usinasController = UsinasController()
eventosController = EventosController()
# analiseController = AnaliseController()
configController = ConfigController()

@app.route("/")
def index():
    print('3- index')
    return homeController.home()

@app.route("/usina/<sigla>")
def usina_page(sigla):
    print('4- usina_page', sigla)
    # carregar métricas / ocorrências da usina
    return usinasController.usina_page(sigla)

@app.route("/registro-eventos")
def registro_eventos():
    print('5- registro_eventos')
    return eventosController.registro_page()

@app.route("/api/ocorrencias", methods=["POST"])
def criar_ocorrencia():
    print('6- criar_ocorrencia')
    return eventosController.criar_ocorrencia()

@app.route("/configuracoes")
def configuracoes():
    print('7- configuracoes')
    return configController.config_page()

@app.route("/configuracoes/salvar", methods=["POST"])
def salvar_configuracao():
    print('8- salvar_configuracao')
    return configController.salvar_configuracao()

@app.route("/configuracoes/carregar", methods=["GET"])
def carregar_configuracao():
    print('9- carregar_configuracao')
    return configController.carregar_configuracao()

# @app.route("/analise-relatorios")
# def analise_relatorios():
#     print('7- analise_relatorios')
#     return analiseController.analise_relatorios()