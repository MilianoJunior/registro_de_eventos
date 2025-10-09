# libs/controllers/analiseController.py
from flask import render_template
from datetime import datetime
from libs.models.utils.utils import desempenho

class AnaliseController:
    def __init__(self):
        self.data = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    @desempenho
    def analise_relatorios(self):
        """Renderiza a página de análise e relatórios"""
        return render_template("analise_relatorios.html", data=self.data)
