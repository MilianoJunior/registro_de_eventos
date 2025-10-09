# libs/controllers/usinasController.py
from flask import render_template
from libs.models.read import Read
from libs.models.mock_data import DEVELOPER_MODE, get_usina_by_sigla
from libs.models.utils.utils import desempenho

class UsinasController:
    def __init__(self):
        self.usinas = Read("op_usina")
    @desempenho
    def usina_page(self, sigla: str):
        """Renderiza a página de detalhes de uma usina específica"""
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            usina = get_usina_by_sigla(sigla)
        else:
            # Usa dados reais do banco de dados
            usina = self.usinas.first({"sigla": sigla})
        
        return render_template("usinas.html", usina=usina, sigla=sigla)
