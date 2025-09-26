from flask import render_template
from libs.models.read import Read

class UsinasController:
    def __init__(self):
        self.usinas = Read('op_usina')

    def usina_page(self, sigla):
        usina = self.usinas.get_by_id(sigla)
        return render_template('usinas.html', usina=usina, sigla=sigla)