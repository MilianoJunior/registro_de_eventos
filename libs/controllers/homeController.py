# libs/controllers/homeController.py
from collections import Counter
from flask import render_template
from libs.models.read import Read
from libs.models.utils.filters import slugify_filter
from libs.models.utils.mock_data import DEVELOPER_MODE, get_estatisticas_home
from libs.models.utils.utils import desempenho
from libs.servicos.readRT import get_data
from libs.sockets.status_usina import coletar_status_usinas


class HomeController:
    def __init__(self):
        # SÃ³ instancia Read se NÃO estiver em modo desenvolvedor
        self.ocorrencias = None if DEVELOPER_MODE else Read("op_ocorrencia")
        self.usinas = None if DEVELOPER_MODE else Read("op_usina")
        self._cache = {}  # cache para dados do banco
        self.developer = True

    @desempenho
    def _get_or_set(self, key, loader):
        """MÃ©todo auxiliar para cache de dados"""
        if key not in self._cache:
            self._cache[key] = loader()
        return self._cache[key]

    @desempenho
    def home(self):
        """Renderiza a pÃ¡gina home com estatÃ­sticas"""
        
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            stats = get_estatisticas_home()
            usinas = stats['usinas']
            recentes = stats['recentes']
            status = stats['status']
            por_unidade = stats['por_unidade']
            total_ocorrencias = stats['total_ocorrencias']
            potencia_total_mw = stats['potencia_total_mw']

            status_operacional_por_usina = {}
            detalhes_status_por_usina = {}
            status_texto_por_usina = {}
            try:
                status_coletados = coletar_status_usinas()
                print(f"[HOME] Status coletados no socket (DEV): {status_coletados}")
                status_operacional_por_usina = {
                    item.get("slug"): item.get("status")
                    for item in status_coletados
                }
                detalhes_status_por_usina = {
                    item.get("slug"): item.get("dispositivos", [])
                    for item in status_coletados
                }
                status_texto_por_usina = {
                    item.get("slug"): item.get("status_texto")
                    for item in status_coletados
                }
            except Exception as exc:
                print(f"[HOME] Erro ao coletar status operacional (DEV): {exc}")

            for usina in usinas:
                slug = slugify_filter(usina.get('nome') or usina.get('sigla'))
                status_atual = status_operacional_por_usina.get(
                    slug,
                    usina.get('status_operacional', 'parada'),
                )
                detalhes = detalhes_status_por_usina.get(slug, [])
                texto_status = status_texto_por_usina.get(slug)
                if not texto_status and detalhes:
                    texto_status = detalhes[0].get("descricao")
                if not texto_status:
                    texto_status = "Status nÃ£o disponÃ­vel"
                usina['status_operacional'] = status_atual
                usina['status_operacional_dispositivos'] = detalhes
                usina['status_operacional_texto'] = texto_status
                print(
                    f"[HOME] (DEV) Aplicando status '{usina['status_operacional']}' "
                    f"para usina '{usina.get('nome')}' (slug='{slug}')"
                )
        else:
            # Usa dados reais do banco de dados
            usinas = self._get_or_set("usinas", lambda: self.usinas.get_all())
            rows = self._get_or_set("ocorrencias", lambda: self.ocorrencias.get_all(limit=20))

            recentes = sorted(rows, key=lambda r: r.get("created_at"), reverse=True)[:10]
            status = Counter((r.get("status") or "-") for r in rows)
            unidades = Counter((r.get("unidade") or "-") for r in rows)
            por_unidade = sorted(unidades.items(), key=lambda x: (-x[1], x[0]))[:8]

            status_operacional_por_usina = {}
            detalhes_status_por_usina = {}
            status_texto_por_usina = {}
            try:
                status_coletados = coletar_status_usinas()
                print(f"[HOME] Status coletados no socket: {status_coletados}")
                status_operacional_por_usina = {
                    item.get("slug"): item.get("status")
                    for item in status_coletados
                }
                detalhes_status_por_usina = {
                    item.get("slug"): item.get("dispositivos", [])
                    for item in status_coletados
                }
                status_texto_por_usina = {
                    item.get("slug"): item.get("status_texto")
                    for item in status_coletados
                }
            except Exception as exc:
                print(f"[HOME] Erro ao coletar status operacional: {exc}")

            for usina in usinas:
                dados = self.get_data_rt(usina)
                slug = slugify_filter(usina.get('nome') or usina.get('sigla'))
                usina['status_operacional'] = status_operacional_por_usina.get(slug, 'parada')
                detalhes = detalhes_status_por_usina.get(slug, [])
                texto_status = status_texto_por_usina.get(slug)
                if not texto_status and detalhes:
                    texto_status = detalhes[0].get("descricao")
                if not texto_status:
                    texto_status = "Status nÃ£o disponÃ­vel"
                usina['status_operacional_dispositivos'] = detalhes
                usina['status_operacional_texto'] = texto_status
                print(
                    f"[HOME] Aplicando status '{usina['status_operacional']}' "
                    f"para usina '{usina.get('nome')}' (slug='{slug}')"
                )
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
            
            # Calcula a potÃªncia ativa total das usinas operando
            potencia_total_mw = sum(u.get('potencia_ativa_mw', 0) for u in usinas if u.get('status_operacional') == 'operando')

        # print('--------------------------------')
        # print('1. usinas')
        # print(' '*5,usinas)
        # print('-'*50)
        # print('2. total_ocorrencias')
        # print(' '*5,total_ocorrencias)
        # print('-'*50)
        # print('3. recentes')
        # print(' '*5,recentes)
        # print('-'*50)
        # print('4. status')
        # print(' '*5,status)
        # print('-'*50)
        # print('5. por_unidade')
        # print(' '*5,por_unidade)
        # print('-'*50)
        # print('6. potencia_total_mw')
        # print(' '*5,potencia_total_mw)
        # print('-'*50)
        # print('--------------------------------')
        

        return render_template("home.html",
            usinas=usinas,
            total_ocorrencias=total_ocorrencias,
            recentes=recentes,
            por_status=dict(status),
            por_unidade=por_unidade,
            potencia_total_mw=potencia_total_mw,
        )

    def get_status_usinas(self):
        ''' ConexÃ£o com a api em tempo real para obter o status operacional de cada UG '''
        return 'parada'
    def get_potencia_usinas(self):
        ''' ConexÃ£o com a api em tempo real para obter a potencia ativa de cada UG '''
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
        ''' Consulta a tabela op_ocorrencia_hist para obter o numero de alarmes de atencao e definir uma classificaÃ§Ã£o de atencao '''
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
7. alarmes_atencao: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes de atencao e definir uma classificaÃ§Ã£o de atencao
8. alarmes_inundantes: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes inundantes
9. alarmes_oscilantes: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes oscilantes
10. energia_nao_gerada_mwh: cria um metodo para consultar a tabela op_ocorrencia_hist para obter a energia nao gerada de cada UG em mwh
11. distribuicao_prioridade: cria um metodo para consultar a tabela op_ocorrencia para obter a distribuicao de prioridade de cada UG
'''
