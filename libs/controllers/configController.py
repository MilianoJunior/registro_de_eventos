# libs/controllers/configController.py
from flask import render_template
from datetime import datetime
from libs.models.read import Read
from libs.models.mock_data import DEVELOPER_MODE, get_mock_data
from libs.models.utils.utils import desempenho

class ConfigController:
    def __init__(self):
        self.usinas = None if DEVELOPER_MODE else Read("op_usina")
    @desempenho
    def config_page(self):
        """Renderiza a página de configuração"""
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            usinas = get_mock_data('op_usina')
        else:
            # Usa dados reais do banco de dados
            usinas = self.usinas.get_all()
        return render_template("configuracoes.html", usinas=usinas)