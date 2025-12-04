from libs.models.read import OpUsina, OpOcorrencia, OpUsuario, OpParadas

class Dados:
    def __init__(self):
        self.usinas = OpUsina()
        self.ocorrencias = OpOcorrencia()
        self.usuarios = OpUsuario()
        self.paradas = OpParadas()
        self.cache = {}

    def get_usinas(self):
        return [usina for usina in self.usinas.get_all()]

    def get_statistics_usinas(self):
        pass

class AbstractEstado:

    usinas = Dados.get_usinas()

    statistics_usinas = [{
        "Potencia Ativa Total MW": stat['potencia_ativa_total_mw'],
        "Ocorrencias Abertas": stat['ocorrencias_abertas'],
        "Em Andamento": stat['em_andamento'],
        "Resolvidas": stat['resolvidas'],
    } for stat in Dados.statistics_usinas()]

    registros_ocorrencias = {
        "Nome_usina": None,
        "Operador": None,
        "Tipo": None,
        "Categoria": None,
        "Unidade": None,
        "Data_ocorrencia": None,
        "Unidade": None,
        "Etiquetas_tags": None,
        "Template": None,
        "Descricao": None,
        "Severidade": None,
        "Playbook": None,
        "requer_acao": None,
    }

    status_usinas = {
        "Nome_usina": None,
        "Sigla": None,
        "Timezone": None,
        "Ativo": None,
        "Status Operacional": None,
        "Potencia Ativa MW": None,
        "MTTR": None,
        "Alarmes Por Hora": None,
        "Alarmes Criticos": None,
        "Incidentes Abertos": None,
        "Alarmes Atencao": None,
        "Alarmes Inundantes": None,
        "Alarmes Oscilantes": None
    }

    alarmes = {
        "Nome_usina": None,
        "Data_ocorrencia": None,
        "Unidade": None,
        "Etiquetas_tags": None,
        "Descricao": None,
        "Severidade": None,
        "Solucao": None,
        "requer_acao": None,
    }

# implementar um sistema de cache para as consultas aos bancos de dados com base temporal para as paginas quando for necessario.

class PaginaHome(AbstractEstado):
    pass

class PaginaOcorrencias(AbstractEstado):
    pass

class PaginaConfiguracoes(AbstractEstado):
    pass

class PaginaUsinas(AbstractEstado):
    pass
''' Todas as classes executam as consultas aos bancos de dados e retornam os dados para as interfaces.'''

'''
[{'id': 1, 'nome': 'CGH-APARECIDA', 'sigla': 'APAR', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993), 'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)}, {'id': 2, 'nome': 'CGH-FAE', 'sigla': 'FAE', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 354315), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 354315)}, {'id': 3, 'nome': 'CGH-HOPPEN', 'sigla': 'HOPP', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 558514), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 558514)}, {'id': 4, 'nome': 'CGH-PICADAS ALTAS', 'sigla': 'PICALT', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 766481), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 766481)}, {'id': 5, 'nome': 'PCH-PEDRAS', 'sigla': 'PEDR', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 969718), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 969718)}]'''