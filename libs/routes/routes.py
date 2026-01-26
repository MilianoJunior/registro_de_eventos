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

from flask import render_template, jsonify, Response, request, send_from_directory
import os
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

from flask import render_template

homeController = HomeController()
usinasController = UsinasController()
ocorrenciasController = OcorrenciasController()
# analiseController = AnaliseController()
configController = ConfigController()
ratsController = RatsController()


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
