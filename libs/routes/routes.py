from flask import render_template, jsonify, Response, request
from main import app
from libs.controllers.homeController import HomeController
from libs.controllers.usinasController import UsinasController

homeController = HomeController()
usinasController = UsinasController()

@app.route("/")
def index():
    print('3- index')
    return homeController.home()

@app.route("/usina/<sigla>")
def usina_page(sigla):
    print('4- usina_page', sigla)
    # carregar métricas / ocorrências da usina
    return usinasController.usina_page(sigla)