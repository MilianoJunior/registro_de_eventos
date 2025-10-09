from flask import render_template, jsonify, Response, request
from main import app
from libs.controllers.homeController import HomeController
from libs.controllers.usinasController import UsinasController
from libs.controllers.eventosController import EventosController
from libs.controllers.analiseController import AnaliseController

from flask import render_template

homeController = HomeController()
usinasController = UsinasController()
eventosController = EventosController()
analiseController = AnaliseController()

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

@app.route("/analise-relatorios")
def analise_relatorios():
    print('7- analise_relatorios')
    return analiseController.analise_relatorios()

@app.route("/novo>")
def novo_modelo():
    # carregar métricas / ocorrências da usina
    return render_template("novo_modelo.html")