# libs/controllers/homeController.py
from collections import Counter
from flask import render_template
from libs.models.read import Read
from libs.models.mock_data import DEVELOPER_MODE, get_estatisticas_home
from libs.models.utils.utils import desempenho

class HomeController:
    def __init__(self):
        self.ocorrencias = Read("op_ocorrencia")
        self.usinas = Read("op_usina")
        self._cache = {}  # cache para dados do banco
        self.developer = True

    @desempenho
    def _get_or_set(self, key, loader):
        """Método auxiliar para cache de dados"""
        if key not in self._cache:
            self._cache[key] = loader()
        return self._cache[key]

    @desempenho
    def home(self):
        """Renderiza a página home com estatísticas"""
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            stats = get_estatisticas_home()
            usinas = stats['usinas']
            recentes = stats['recentes']
            status = stats['status']
            por_unidade = stats['por_unidade']
            total_ocorrencias = stats['total_ocorrencias']
            potencia_total_mw = stats['potencia_total_mw']
        else:
            # Usa dados reais do banco de dados
            usinas = self._get_or_set("usinas", lambda: self.usinas.get_all())
            rows = self._get_or_set("ocorrencias", lambda: self.ocorrencias.get_all(limit=20))

            recentes = sorted(rows, key=lambda r: r.get("created_at"), reverse=True)[:10]
            status = Counter((r.get("status") or "-") for r in rows)
            unidades = Counter((r.get("unidade") or "-") for r in rows)
            por_unidade = sorted(unidades.items(), key=lambda x: (-x[1], x[0]))[:8]
            for usina in usinas:
                usina['status_operacional'] = 'operando' 
                usina['potencia_ativa_mw'] = 1200
                usina['mttr'] = '13h min'
                usina['alarmes_por_hora'] = 8.0
                usina['alarmes_criticos'] = 0
                usina['incidentes_abertos'] = 0
                usina['alarmes_atencao'] = 3
                usina['alarmes_inundantes'] = 0
                usina['alarmes_oscilantes'] = 2
                usina['energia_nao_gerada_mwh'] = 0
                usina['distribuicao_prioridade'] = {'alta': 0, 'media': 100, 'baixa': 0}
                
            total_ocorrencias = len(rows)
            
            # Calcula a potência ativa total das usinas operando
            potencia_total_mw = sum(u.get('potencia_ativa_mw', 0) for u in usinas if u.get('status_operacional') == 'operando')

        print('--------------------------------')
        print('1. usinas')
        print(' '*5,usinas)
        print('-'*50)
        print('2. total_ocorrencias')
        print(' '*5,total_ocorrencias)
        print('-'*50)
        print('3. recentes')
        print(' '*5,recentes)
        print('-'*50)
        print('4. status')
        print(' '*5,status)
        print('-'*50)
        print('5. por_unidade')
        print(' '*5,por_unidade)
        print('-'*50)
        print('6. potencia_total_mw')
        print(' '*5,potencia_total_mw)
        print('-'*50)
        print('--------------------------------')

        return render_template("home.html",
            usinas=usinas,
            total_ocorrencias=total_ocorrencias,
            recentes=recentes,
            por_status=dict(status),
            por_unidade=por_unidade,
            potencia_total_mw=potencia_total_mw,
        )
    def get_status_usinas(self):
        ''' Conexão com a api em tempo real para obter o status operacional de cada UG '''
        return 'operando'
    def get_potencia_usinas(self):
        ''' Conexão com a api em tempo real para obter a potencia ativa de cada UG '''
        return 1200

    def get_mttr_usinas(self):
        ''' Consulta a tabela op_ocorrencia_hist para obter o mttr de cada UG '''
        return '13h min'
    def get_alarmes_por_hora_usinas(self):
        ''' Consulta a tabela op_ocorrencia_hist para obter o numero de alarmes por hora de cada UG '''
        return 8.0
    def get_alarmes_criticos_usinas(self):
        ''' Consulta a tabela op_ocorrencia_hist para obter o numero de alarmes criticos de cada UG '''
        return 0
    def get_incidentes_abertos_usinas(self):
        ''' Consulta a tabela op_ocorrencia_hist para obter o numero de incidentes abertos '''
        return 0
    def get_alarmes_atencao_usinas(self):
        ''' Consulta a tabela op_ocorrencia_hist para obter o numero de alarmes de atencao e definir uma classificação de atencao '''
        return 3
    def get_alarmes_inundantes_usinas(self):
        ''' Consulta a tabela op_ocorrencia_hist para obter o numero de alarmes inundantes '''
        return 0
    def get_alarmes_oscilantes_usinas(self):
        ''' Consulta a tabela op_ocorrencia_hist para obter o numero de alarmes oscilantes '''
        return 2
    def get_energia_nao_gerada_mwh_usinas(self):
        ''' Consulta a tabela op_ocorrencia_hist para obter a energia nao gerada de cada UG em mwh '''
        return 0
    def get_distribuicao_prioridade_usinas(self):
        ''' Consulta a tabela op_ocorrencia para obter a distribuicao de prioridade de cada UG '''
        return {'alta': 0, 'media': 100, 'baixa': 0}


'''
1. status_operacional: usar a api em tempo real para obter o status operacional de cada UG
2. potencia_ativa_mw: usar a api em tempo real para obter a potencia ativa de cada UG 
3. mttr: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o mttr de cada UG
4. alarmes_por_hora: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes por hora de cada UG
5. alarmes_criticos: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes criticos de cada UG
6. incidentes_abertos: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de incidentes abertos
7. alarmes_atencao: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes de atencao e definir uma classificação de atencao
8. alarmes_inundantes: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes inundantes
9. alarmes_oscilantes: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes oscilantes
10. energia_nao_gerada_mwh: cria um metodo para consultar a tabela op_ocorrencia_hist para obter a energia nao gerada de cada UG em mwh
11. distribuicao_prioridade: cria um metodo para consultar a tabela op_ocorrencia para obter a distribuicao de prioridade de cada UG
'''