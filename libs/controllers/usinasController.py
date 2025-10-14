# libs/controllers/usinasController.py
from flask import render_template
from libs.models.read import Read
from libs.models.mock_data import (
    DEVELOPER_MODE, 
    get_usina_by_sigla, 
    get_mock_data,
    get_ocorrencias_por_usina,
    get_timeline_vertedouro
)
from libs.models.utils.utils import desempenho
import json

class UsinasController:
    def __init__(self):
        self.usinas = Read("op_usina")
        self.ocorrencias = Read("op_ocorrencia")
    
    def _decode_metadata(self, ocorrencias):
        """Decodifica o campo metadata JSON para cada ocorrência"""
        for ocorrencia in ocorrencias:
            if ocorrencia.get('metadata'):
                try:
                    if isinstance(ocorrencia['metadata'], str):
                        ocorrencia['metadata'] = json.loads(ocorrencia['metadata'])
                except (json.JSONDecodeError, TypeError):
                    ocorrencia['metadata'] = {}
            else:
                ocorrencia['metadata'] = {}
        return ocorrencias
        
    @desempenho
    def usina_page(self, sigla: str):
        """Renderiza a página de detalhes de uma usina específica"""
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            usina = get_usina_by_sigla(sigla)
            usinas = get_mock_data('op_usina')
            
            # Busca TODAS as ocorrências da usina para a timeline filtrada
            timeline_filtrada = get_ocorrencias_por_usina(usina['id'], limit=50)
            timeline_filtrada = self._decode_metadata(timeline_filtrada)
        else:
            # Usa dados reais do banco de dados
            usina = self.usinas.first({"sigla": sigla})
            usinas = self.usinas.get_all()
            
            # Adiciona campos mock temporariamente (serão substituídos por dados reais)
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
            
            # Busca TODAS as ocorrências da usina para a timeline filtrada
            timeline_filtrada = self.ocorrencias.where(
                where={"usina_id": usina['id']},
                limit=50,
                order_by="created_at",
                desc=True
            )
            
            # Decodifica metadata JSON
            timeline_filtrada = self._decode_metadata(timeline_filtrada)
            
        print('--------------------------------')
        print('usina')
        print(usina)
        print('--------------------------------')
        print('timeline_filtrada')
        print(timeline_filtrada)
        print('--------------------------------')

        return render_template(
            "usinas.html", 
            usina=usina, 
            usinas=usinas, 
            sigla=sigla,
            timeline_filtrada=timeline_filtrada
        )
