# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. usina_page → Renderiza a página de detalhes da usina (UsinasPageViewModel)
# -------------------------------------------------------------------

from flask import render_template, request
from libs.models.modelstate import UsinasPageViewModel, DadosContexto
from libs.controllers.decorador import desempenho

class UsinasController:
    def __init__(self):
        pass
        
    @desempenho
    def usina_page(self, sigla: str):
        """Renderiza a página de detalhes de uma usina específica"""
        ctx = DadosContexto()
        data_inicio = (request.args.get("data_inicio") or "").strip()
        data_fim = (request.args.get("data_fim") or "").strip()
        vm = UsinasPageViewModel.carregar(ctx, sigla, data_inicio=data_inicio, data_fim=data_fim, limit=30)

        return render_template(
            "usinas.html", 
            usina=vm.usina, 
            usinas=vm.usinas, 
            sigla=vm.sigla,
            timeline_filtrada=vm.timeline_filtrada,
            vm=vm # Passando VM completo caso o template precise no futuro
        )
