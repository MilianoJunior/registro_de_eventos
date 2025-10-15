# libs/controllers/analiseController.py
from flask import render_template
from datetime import datetime
from libs.models.read import Read
from libs.models.mock_data import DEVELOPER_MODE, get_mock_data
from libs.models.utils.utils import desempenho

class AnaliseController:
    def __init__(self):
        self.data = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.usinas = Read("op_usina")

    @desempenho
    def analise_relatorios(self):
        """Renderiza a página de análise e relatórios"""
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            usinas = get_mock_data('op_usina')
        else:
            # Usa dados reais do banco de dados
            usinas = self.usinas.get_all()
        
        return render_template("analise_relatorios.html", data=self.data, usinas=usinas)
