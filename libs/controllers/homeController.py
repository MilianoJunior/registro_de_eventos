# libs/controllers/homeController.py
from flask import render_template
from libs.controllers.decorador import desempenho
from libs.models.modelstate import DadosContexto, HomePageViewModel
import time

class HomeController:
    @desempenho
    def home(self):
        """Renderiza a página home usando o ViewModel centralizado"""
        
        inicio = time.time()
        # 1. Cria Contexto (busca dados + cache)
        ctx = DadosContexto()
        
        # 2. Carrega ViewModel
        vm = HomePageViewModel.carregar(ctx)
        
        fim = time.time()
        print(f"homeController.home - Tempo de execução: {fim - inicio} segundos")
        # 3. Renderiza
        # Passamos 'vm' para o template, mas também desconstruímos 
        # para manter compatibilidade com variáveis existentes no HTML se necessário
        print("VM", vm)
        print(" ")
        print("Usinas", vm.usinas)
        print(" ")
        print("Ocorrencias Recentes", vm.ocorrencias_recentes)
        print(" ")
        print("Total Ocorrencias", vm.total_ocorrencias)
        print(" ")
        print("Potencia Total MW", vm.potencia_total_mw)
        print(" ")
        print("Por Status", vm.stats_por_status)
        print(" ")
        print("Por Unidade", vm.stats_por_unidade)
        print('-' * 50)
        print("")
        return render_template("home.html",
            vm=vm,
            # usinas=vm.usinas,
            # ocorrencias=vm.ocorrencias_recentes, # Alias para loops antigos
            # recentes=vm.ocorrencias_recentes,
            # total_ocorrencias=vm.total_ocorrencias,
            # potencia_total_mw=vm.potencia_total_mw,
            # por_status=vm.stats_por_status,
            # por_unidade=vm.stats_por_unidade,
            # mttr_diario=[] # Depreciado
        )
# O código antigo e placeholders foram removidos pois agora
# a lógica está encapsulada em HomePageViewModel e DadosContexto.

