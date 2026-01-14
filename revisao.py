# Rotas
from libs.controllers.ratsController import RatsController

ratsController = RatsController()

@app.route('/rats')
def rats():
    return ratsController.inforat()

@app.route('/criarrat')
def criarrat():
    return ratsController.criarrat()

@app.route('/rat/salvar', methods=['POST'])
def salvar_rat():
    return ratsController.salvarrat()

@app.route('/rat/upload_foto', methods=['POST'])
def upload_foto():
    return ratsController.upload_foto()

@app.route('/rat/ver/<int:rat_id>', methods=['GET'])
def ver_rat(rat_id):
    return ratsController.ver_rat(rat_id)

@app.route('/modificarrat', defaults={'rat_id': None})
@app.route('/modificarrat/<int:rat_id>')
def modificarrat(rat_id):
    return ratsController.modificarrat(rat_id)

@app.route('/produtos/buscar', methods=['GET'])
def buscar_produtos():
    return ratsController.buscar_produtos()

@app.route('/rat/atualizar', methods=['POST'])
def atualizar_rat():
    return ratsController.atualizar_rat()

@app.route('/rat/atualizar_status_financeiro', methods=['POST'])
def atualizar_status_financeiro():
    return ratsController.atualizar_status_financeiro()

@app.route('/rat/deletar', methods=['POST'])
def deletar_rat():
    return ratsController.deletar_rat()

@app.route('/rat/pdf/<int:rat_id>', methods=['GET'])
def gerar_pdf(rat_id):
    return ratsController.gerar_pdf(rat_id)
# Models

from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from libs.models.database import Database


class BaseCrud:
    """Classe base para operações CRUD genéricas."""

    tabela: str
    colunas: List[str]

    def __init__(self) -> None:
        self.db = Database()
        self._colunas_set = set(self.colunas)

    def _validate_columns(self, columns: Union[str, List[str]]) -> List[str]:
        """Valida e normaliza lista de colunas. Suporta '*' para todas as colunas."""
        if columns == "*" or columns == ["*"]:
            return self.colunas[:]

        if isinstance(columns, str):
            columns = [columns]

        columns = [col.strip() for col in columns]
        if not all(col in self._colunas_set for col in columns):
            raise ValueError(f"Colunas inválidas: {set(columns) - self._colunas_set}")
        return columns

    def read(
        self,
        columns: Union[str, List[str]] = "*",
        where: Optional[str] = None,
        where_params: Optional[Sequence[Any]] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Busca registros com colunas selecionadas."""
        columns = self._validate_columns(columns)
        query = f"SELECT {', '.join(columns)} FROM {self.tabela}"

        params: List[Any] = []
        if where:
            query += f" WHERE {where}"
            if where_params:
                params.extend(where_params)

        if order:
            query += f" ORDER BY {order}"
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        return self.db.fetch_data(query, tuple(params))

    def create(self, data: Dict[str, Any]) -> int:
        """Insere um novo registro e retorna o número de linhas afetadas."""
        valid_data = {k: v for k, v in data.items() if k in self._colunas_set}
        if not valid_data:
            raise ValueError("Nenhum dado válido para inserir")

        columns = ', '.join(valid_data.keys())
        placeholders = ', '.join(['%s'] * len(valid_data))
        query = f"INSERT INTO {self.tabela} ({columns}) VALUES ({placeholders})"

        return self.db.execute_query(query, tuple(valid_data.values()))

    def update(
        self,
        data: Dict[str, Any],
        where: str,
        where_params: Optional[Sequence[Any]] = None,
    ) -> int:
        """Atualiza registros conforme cláusula WHERE."""
        valid_data = {k: v for k, v in data.items() if k in self._colunas_set}
        if not valid_data:
            raise ValueError("Nenhum dado válido para atualizar")

        set_clause = ', '.join(f"{k} = %s" for k in valid_data.keys())
        query = f"UPDATE {self.tabela} SET {set_clause} WHERE {where}"

        params = list(valid_data.values())
        if where_params:
            params.extend(where_params)

        return self.db.execute_query(query, tuple(params))

    def delete(
        self,
        where: str,
        where_params: Optional[Sequence[Any]] = None,
    ) -> int:
        """Remove registros conforme cláusula WHERE."""
        if not where:
            raise ValueError("Cláusula WHERE é obrigatória para DELETE")

        query = f"DELETE FROM {self.tabela} WHERE {where}"
        return self.db.execute_query(query, tuple(where_params) if where_params else None)

    def count(
        self,
        where: Optional[str] = None,
        where_params: Optional[Sequence[Any]] = None,
    ) -> int:
        """Retorna a contagem de registros."""
        query = f"SELECT COUNT(*) AS total FROM {self.tabela}"
        params: List[Any] = []

        if where:
            query += f" WHERE {where}"
            if where_params:
                params.extend(where_params)

        result = self.db.fetch_data(query, tuple(params))
        return result[0]["total"] if result else 0


# ====================== Classes específicas ======================

class Clientes(BaseCrud):
    tabela = "clientes"
    colunas = ["id", "nome_razao", "cnpj", "cidade", "obras"]


class Usuarios(BaseCrud):
    tabela = "op_usuario"
    colunas = ["id", "nome", "email", "perfil", "ativo", "cargo", "assinatura"]


class Rat(BaseCrud):
    tabela = "rats"
    colunas = [
        "id", "protocolo", "data_emissao", "cliente_id", "obra_nome",
        "num_proposta", "num_contrato", "data_solicitacao", "solicitante",
        "tipo_atividade", "prioridade", "em_garantia", "relato_cliente",
        "tecnico_id", "descricao_atividades", "conclusao",
        "caminho_assinatura_tec", "caminho_assinatura_cli", "status_financeiro", "deslocamento"
    ]

    # Métodos específicos (todos parametrizados quando possível)
    def get_total_rats_month(self) -> int:
        query = """
            SELECT COUNT(*) AS total 
            FROM rats 
            WHERE MONTH(data_emissao) = MONTH(CURRENT_DATE()) 
              AND YEAR(data_emissao) = YEAR(CURRENT_DATE())
        """
        res = self.db.fetch_data(query)
        return res[0]["total"] if res else 0

    def get_total_hours_month(self) -> float:
        query = """
            SELECT COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(s.hora_fim, s.hora_inicio))) / 3600, 0) AS total_hours
            FROM rat_servicos s
            JOIN rats r ON s.rat_id = r.id
            WHERE MONTH(r.data_emissao) = MONTH(CURRENT_DATE())
              AND YEAR(r.data_emissao) = YEAR(CURRENT_DATE())
        """
        res = self.db.fetch_data(query)
        return float(res[0]["total_hours"]) if res else 0.0

    def get_top_plant_hours(self) -> Optional[Dict[str, Any]]:
        query = """
            SELECT r.obra_nome,
                   COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(s.hora_fim, s.hora_inicio))) / 3600, 0) AS total_hours
            FROM rats r
            JOIN rat_servicos s ON r.id = s.rat_id
            GROUP BY r.obra_nome
            ORDER BY total_hours DESC
            LIMIT 1
        """
        res = self.db.fetch_data(query)
        return res[0] if res else None

    def get_rats_with_hours_paginated(self, limit: int, offset: int, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        where_clause = ""
        params = []
        
        if search_term:
            term = f"%{search_term}%"
            where_clause = "WHERE (r.protocolo LIKE %s OR r.obra_nome LIKE %s OR r.solicitante LIKE %s OR r.relato_cliente LIKE %s)"
            params.extend([term, term, term, term])

        query = f"""
            SELECT r.*,
                   COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(s.hora_fim, s.hora_inicio))) / 3600, 0) AS total_horas
            FROM {self.tabela} r
            LEFT JOIN rat_servicos s ON r.id = s.rat_id
            {where_clause}
            GROUP BY r.id
            ORDER BY r.data_emissao DESC, r.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return self.db.fetch_data(query, tuple(params))

    def get_average_time_rat(self) -> float:
        query = """
            SELECT AVG(rat_hours) AS avg_hours
            FROM (
                SELECT SUM(TIME_TO_SEC(TIMEDIFF(hora_fim, hora_inicio))) / 3600 AS rat_hours
                FROM rat_servicos
                GROUP BY rat_id
            ) AS subquery
        """
        res = self.db.fetch_data(query)
        return float(res[0]["avg_hours"]) if res and res[0]["avg_hours"] is not None else 0.0

    def get_pending_signatures_count(self) -> int:
        query = """
            SELECT COUNT(*) AS total
            FROM rats
            WHERE caminho_assinatura_tec IS NULL OR caminho_assinatura_tec = ''
               OR caminho_assinatura_cli IS NULL OR caminho_assinatura_cli = ''
        """
        res = self.db.fetch_data(query)
        return res[0]["total"] if res else 0

    def get_priority_distribution(self) -> List[Dict[str, Any]]:
        query = f"SELECT prioridade, COUNT(*) AS count FROM {self.tabela} WHERE prioridade IS NOT NULL GROUP BY prioridade"
        return self.db.fetch_data(query)

    def get_activity_list(self) -> List[Dict[str, Any]]:
        query = f"""
            SELECT tipo_atividade, COUNT(*) AS count
            FROM {self.tabela}
            WHERE tipo_atividade IS NOT NULL
            GROUP BY tipo_atividade
            ORDER BY count DESC
        """
        return self.db.fetch_data(query)

    def get_tech_hours(self) -> List[Dict[str, Any]]:
        query = """
            SELECT u.nome,
                   COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(s.hora_fim, s.hora_inicio))) / 3600, 0) AS total_hours
            FROM rat_servicos s
            JOIN op_usuario u ON s.executante_id = u.id
            GROUP BY u.nome
            ORDER BY total_hours DESC
        """
        return self.db.fetch_data(query)

    def get_top_clients(self) -> List[Dict[str, Any]]:
        query = """
            SELECT obra_nome, COUNT(*) AS count
            FROM rats
            WHERE obra_nome IS NOT NULL
            GROUP BY obra_nome
            ORDER BY count DESC
            LIMIT 5
        """
        return self.db.fetch_data(query)

    def get_by_id_with_details(self, rat_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT r.*, 
                   c.nome_razao AS cliente_nome, 
                   c.cnpj AS cliente_cnpj, 
                   c.cidade AS cliente_cidade,
                   u.nome AS tecnico_nome
            FROM rats r
            LEFT JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN op_usuario u ON r.tecnico_id = u.id
            WHERE r.id = %s
        """
        res = self.db.fetch_data(query, (rat_id,))
        return res[0] if res else None


class RatServicos(BaseCrud):
    tabela = "rat_servicos"
    colunas = ["id", "rat_id", "data_servico", "hora_inicio", "hora_fim", "executante_id", "observacoes"]

    def get_by_rat_id_with_executante(self, rat_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT s.*, u.nome AS executante_nome
            FROM rat_servicos s
            LEFT JOIN op_usuario u ON s.executante_id = u.id
            WHERE s.rat_id = %s
        """
        return self.db.fetch_data(query, (rat_id,))

class RatMateriais(BaseCrud):
    tabela = "rat_materiais"
    colunas = ["id", "rat_id", "codigo_engesep", "descricao", "fabricante", "quantidade", "unidade"]


class RatFotos(BaseCrud):
    tabela = "rat_fotos"
    colunas = ["id", "rat_id", "caminho_arquivo", "legenda", "ordem"]


class Produtos(BaseCrud):
    tabela = "produtos"
    colunas = ["id", "codigo_produto", "descricao", "unidade", "marca", "preco_venda"]

    def search_by_term(self, term: str, limit: int = 20) -> List[Dict[str, Any]]:
        safe_term = term.replace("'", "''")  # escape básico
        query = f"""
            SELECT * FROM {self.tabela}
            WHERE descricao LIKE %s OR codigo_produto LIKE %s
            LIMIT %s
        """
        pattern = f"%{safe_term}%"
        return self.db.fetch_data(query, (pattern, pattern, limit))
# Controllers

from flask import render_template, request, make_response
from libs.models.rats_crud import Clientes, Usuarios, Rat, RatServicos, RatMateriais, RatFotos, Produtos
import json
from datetime import datetime
from libs.models.utils.utils import format_date_br, format_time_hm, format_float_hours, format_duration_str
import uuid
from werkzeug.utils import secure_filename
import os
import base64
from libs.models.modelstate import DadosContexto
from weasyprint import HTML


def gerar_pdf_bytes(html_content, base_url=None):
    try:
        pdf_file = HTML(string=html_content, base_url=base_url).write_pdf()
        return pdf_file
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        raise e

class RatsController:
    def __init__(self):
        self.clientes_model = Clientes()
        self.usuarios_model = Usuarios()
        self.rat_model = Rat()
        self.rat_servicos_model = RatServicos()
        self.rat_materiais_model = RatMateriais()
        self.rat_fotos_model = RatFotos()
        self.produtos_model = Produtos()
        self.dados_contexto = DadosContexto()


    def save_base64_image(self, base64_str, subfolder, filename):
        if not base64_str or "base64," not in base64_str:
            return ""
        
        try:
            # Extract data
            header, encoded = base64_str.split(",", 1)
            data = base64.b64decode(encoded)
            
            # Create directory
            save_dir = os.path.join(os.getcwd(), 'assets', 'RAT', subfolder)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            file_path = os.path.join(save_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(data)
                
            return f"/assets/RAT/{subfolder}/{filename}"
        except Exception as e:
            print(f"Erro ao salvar imagem {filename}: {e}")
            return ""

    def inforat(self):
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '').strip()
        per_page = 10
        offset = (page - 1) * per_page
        
        # Build count where clause
        where_count = None
        params_count = None
        if search_query:
            term = f"%{search_query}%"
            where_count = "(protocolo LIKE %s OR obra_nome LIKE %s OR solicitante LIKE %s OR relato_cliente LIKE %s)"
            params_count = [term, term, term, term]

        total_rats = self.rat_model.count(where=where_count, where_params=params_count)
        total_pages = (total_rats + per_page - 1) // per_page
        
        lista_rats = self.rat_model.get_rats_with_hours_paginated(limit=per_page, offset=offset, search_term=search_query)
        
        usuarios = self.usuarios_model.read(['id', 'nome'])
        mapa_tecnicos = {u['id']: u['nome'] for u in usuarios}
        
        for rat in lista_rats:
            t_id = rat.get('tecnico_id')
            rat['tecnico_nome'] = mapa_tecnicos.get(t_id, 'N/A')
            
            rat['data_formatada'] = format_date_br(rat.get('data_emissao'))
            rat['total_horas'] = format_float_hours(rat.get('total_horas', 0))

        if request.args.get('partial'):
            return render_template(
                'components/_tabela_rats.html',
                lista_rats=lista_rats,
                current_page=page,
                total_pages=total_pages
            )
            
        # Buscar KPIs
        kpis = {
            'total_rats_month': self.rat_model.get_total_rats_month(),
            'total_hours_month': round(self.rat_model.get_total_hours_month(), 1),
            'top_plant': self.rat_model.get_top_plant_hours(),
            'avg_time_rat': self.rat_model.get_average_time_rat(),
            'pending_signatures': self.rat_model.get_pending_signatures_count()
        }
        
        # Formatar tempo médio em H e M
        kpis['avg_time_str'] = format_duration_str(kpis['avg_time_rat'])

        # Dados para Gráficos
        priority_data = self.rat_model.get_priority_distribution()
        activity_data = self.rat_model.get_activity_list()
        tech_hours_data = self.rat_model.get_tech_hours()
        top_clients_data = self.rat_model.get_top_clients()

        # Calcular porcentagens para barra de progresso
        if top_clients_data:
            max_count = top_clients_data[0]['count']
            for client in top_clients_data:
                client['percentage'] = (client['count'] / max_count) * 100

        charts = {
            'priority': {
                'labels': [p['prioridade'] for p in priority_data],
                'data': [p['count'] for p in priority_data]
            },
            'activity': {
                'labels': [a['tipo_atividade'] for a in activity_data],
                'data': [a['count'] for a in activity_data]
            },
            'tech_hours': {
                'labels': [t['nome'].split()[0] for t in tech_hours_data], # First name only
                'data': [float(t['total_hours']) for t in tech_hours_data]
            }
        }

        # Nome do mês atual
        meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        current_month = meses[datetime.now().month]
        
        usinas = self.dados_contexto.get_usinas()

        return render_template(
            'rats.html', 
            page='inforat',
            lista_rats=lista_rats,
            current_page=page,
            total_pages=total_pages,
            kpis=kpis,
            charts=json.dumps(charts), # Serialize for JS
            current_month=current_month,
            top_clients=top_clients_data,
            usinas=usinas,
            search_query=search_query
        )
        
    def criarrat(self):
        lista_clientes = self.clientes_model.read(['*'])
        lista_usuarios = self.usuarios_model.read(['id', 'nome', 'cargo'])
        clientes_json = json.dumps(lista_clientes)
        protocolo = self.gerarprotocolo()
        usinas = self.dados_contexto.get_usinas()

        return render_template(
            'rats.html', 
            clientes=lista_clientes, 
            usuarios=lista_usuarios,
            clientes_json=clientes_json,
            protocolo=protocolo,
            data_atual=datetime.now().strftime('%Y-%m-%d'),
            page='criarrat',
            usinas=usinas
        )
    def salvarrat(self):
        try:
            data = request.json
            if not data:
                return {'status': 'error', 'message': 'Dados não fornecidos'}, 400

            # Capturar o Técnico Responsável (primeiro executante dos serviços)
            servicos = data.get('servicos', [])
            tecnico_id = None
            if servicos and len(servicos) > 0:
                tecnico_id = servicos[0].get('executante_id')

            # 1. Salvar RAT
            rat_data = {
                'protocolo': data.get('protocolo'),
                'data_emissao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'cliente_id': data.get('cliente_id'),
                'obra_nome': data.get('obra_nome'),
                'data_solicitacao': data.get('data_solicitacao'),
                'solicitante': data.get('solicitante'),
                'tipo_atividade': data.get('tipo_atividade'),
                'prioridade': data.get('prioridade'),
                'em_garantia': 1 if data.get('em_garantia') else 0,
                'relato_cliente': data.get('relato_cliente'),
                'descricao_atividades': data.get('descricao_atividades'),
                'conclusao': data.get('conclusao'),
                'tecnico_id': tecnico_id,
                'caminho_assinatura_tec': self.save_base64_image(data.get('assinatura_tecnico'), 'signatures', f"sig_{data.get('protocolo')}_tec.png"),
                'caminho_assinatura_cli': self.save_base64_image(data.get('assinatura_cliente'), 'signatures', f"sig_{data.get('protocolo')}_cli.png"),
                'status_financeiro': 'nao_faturavel' if data.get('em_garantia') else 'pendente_faturamento',
                'deslocamento': data.get('deslocamento')
            }
            sucesso = self.rat_model.create(rat_data)
            
            if not sucesso:
                return {'status': 'error', 'message': 'Erro ao criar RAT no banco'}, 500

            # Recuperar ID do RAT recém criado pelo protocolo (que deve ser único)
            rat_criada = self.rat_model.read(['id'], where=f"protocolo = '{rat_data['protocolo']}'")
            if not rat_criada:
                 return {'status': 'error', 'message': 'RAT criada mas não encontrada'}, 500
            
            rat_id = rat_criada[0]['id']

            # 2. Salvar Horas (Serviços)
            servicos = data.get('servicos', [])
            for svc in servicos:
                svc_data = {
                    'rat_id': rat_id,
                    'data_servico': svc.get('data'),
                    'hora_inicio': svc.get('hora_inicio'),
                    'hora_fim': svc.get('hora_fim'),
                    'executante_id': svc.get('executante_id'),
                    'observacoes': svc.get('observacoes')
                }
                self.rat_servicos_model.create(svc_data)

            materiais = data.get('materiais', [])
            for mat in materiais:
                mat_data = {
                    'rat_id': rat_id,
                    'codigo_engesep': mat.get('codigo'),
                    'descricao': mat.get('descricao'),
                    'fabricante': mat.get('fabricante'),
                    'quantidade': mat.get('quantidade'),
                    'unidade': mat.get('unidade')
                }
                self.rat_materiais_model.create(mat_data)

            fotos = data.get('fotos', [])
            for foto in fotos:
                foto_data = {
                    'rat_id': rat_id,
                    'caminho_arquivo': foto.get('caminho'),
                    'legenda': foto.get('legenda'),
                    'ordem': 0 
                }
                self.rat_fotos_model.create(foto_data)

            return {'status': 'success', 'message': 'RAT criada com sucesso', 'id': rat_id, 'protocolo': rat_data['protocolo']}, 200

        except Exception as e:
            print(f"Erro no controller salvarrat: {e}")
            return {'status': 'error', 'message': str(e)}, 500

    

    def upload_foto(self):
        if 'file' not in request.files:
            return {'status': 'error', 'message': 'Nenhum arquivo enviado'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'status': 'error', 'message': 'Nenhum arquivo selecionado'}, 400
        
        if file:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Ajustar caminho para assets/RAT/imgs
            upload_folder = os.path.join(os.getcwd(), 'assets', 'RAT', 'imgs')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Caminho para acesso via web
            relative_path = f"/assets/RAT/imgs/{unique_filename}"
            return {'status': 'success', 'url': relative_path}, 200

    def ver_rat(self, rat_id):
        try:
            rat_data = self.rat_model.get_by_id_with_details(rat_id)
            if not rat_data:
                 return {'status': 'error', 'message': 'RAT não encontrada'}, 404
            
            servicos = self.rat_servicos_model.get_by_rat_id_with_executante(rat_id)
            
            materiais = self.rat_materiais_model.read(['*'], where=f"rat_id = {rat_id}")

            fotos = self.rat_fotos_model.read(['*'], where=f"rat_id = {rat_id}", order='ordem')
            
            # Formatações de Data
            rat_data['data_emissao'] = format_date_br(rat_data.get('data_emissao'))
            rat_data['data_solicitacao'] = format_date_br(rat_data.get('data_solicitacao'))

            # Formatações de Horas nos Serviços
            for svc in servicos:
                svc['data_servico'] = format_date_br(svc.get('data_servico'))
                svc['hora_inicio'] = format_time_hm(svc.get('hora_inicio'))
                svc['hora_fim'] = format_time_hm(svc.get('hora_fim'))

            response_data = {
                'rat': rat_data,
                'servicos': servicos,
                'materiais': materiais,
                'fotos': fotos
            }
            
            return response_data, 200

        except Exception as e:
            print(f"Erro em ver_rat: {e}")
            return {'status': 'error', 'message': str(e)}, 500

    def buscar_produtos(self):
        query = request.args.get('q', '').strip()
        if not query:
            return {'results': []}, 200
        
        try:
            results = self.produtos_model.search_by_term(query, limit=20)
            return {'results': results}, 200
        except Exception as e:
            print(f"Erro na busca de produtos: {e}")
            return {'results': []}, 500

    def modificarrat(self, rat_id=None):

        usinas = self.dados_contexto.get_usinas()
        if rat_id:
            rat_data = self.rat_model.read(['*'], where=f"id = {rat_id}")
            if rat_data:
                rat = rat_data[0]
                if rat.get('data_emissao'):
                    rat['data_emissao'] = str(rat['data_emissao'])
                if rat.get('data_solicitacao'):
                     if isinstance(rat['data_solicitacao'], str):
                         rat['data_solicitacao'] = rat['data_solicitacao'].split(' ')[0]
                     else:
                        rat['data_solicitacao'] = rat['data_solicitacao'].strftime('%Y-%m-%d')

                servicos = self.rat_servicos_model.read(['*'], where=f"rat_id = {rat_id}")
                
                 # Fetch users and convert to dictionary for easy access if needed, but list is fine for select
                usuarios = self.usuarios_model.read(['id', 'nome'], where="ativo=1")

                # Pre-process services to format time for input type="time" (HH:MM)
                for svc in servicos:
                    svc['hora_inicio'] = format_time_hm(svc.get('hora_inicio'))
                    svc['hora_fim'] = format_time_hm(svc.get('hora_fim'))

                materiais = self.rat_materiais_model.read(['*'], where=f"rat_id = {rat_id}")
                fotos = self.rat_fotos_model.read(['*'], where=f"rat_id = {rat_id}", order='ordem')

                return render_template(
                    'rats.html', 
                    page='modificarrat',
                    rat=rat,
                    servicos=servicos,
                    materiais=materiais,
                    fotos=fotos,
                    usuarios=usuarios,
                    usinas=usinas
                )
        

        return render_template(
            'rats.html', 
            page='modificarrat',
            rat=None,
            usinas=usinas
        )

    def gerarprotocolo(self):
        data_atual = datetime.now().strftime('%Y%m%d')
        numero_protocolo = f'{data_atual}'
        numero_sequencial = self.rat_model.read(['id'], order='id DESC', limit=1)
        if numero_sequencial:
            numero_sequencial = numero_sequencial[0]['id'] + 1
        else:
            numero_sequencial = 1
        protocolo = f'{numero_protocolo}-{numero_sequencial:02d}'
        return protocolo

    def atualizar_rat(self):
        try:
            data = request.json
            rat_id = data.get('rat_id')
            if not rat_id:
                return {'message': 'ID do RAT não fornecido'}, 400

            # 1. Atualizar RAT (Informações Descritivas)
            rat_update = {
                'descricao_atividades': data.get('descricao_atividades'),
                'conclusao': data.get('conclusao'),
                'deslocamento': data.get('deslocamento')
            }
            self.rat_model.update(rat_update, where=f"id = {rat_id}")

            # 2. Atualizar Serviços (Delete all for RAT and Re-insert)
            self.rat_servicos_model.delete(where=f"rat_id = {rat_id}")
            
            servicos = data.get('servicos', [])
            if servicos:
                for svc in servicos:
                    # Validate mandatory fields
                    if svc.get('data') and svc.get('inicio') and svc.get('fim'):
                        self.rat_servicos_model.create({
                            'rat_id': rat_id,
                            'data_servico': svc['data'],
                            'hora_inicio': svc['inicio'],
                            'hora_fim': svc['fim'],
                            'executante_id': svc.get('executante') 
                        })

            # 3. Atualizar Materiais (Delete all and Re-insert)
            self.rat_materiais_model.delete(where=f"rat_id = {rat_id}")
            
            materiais = data.get('materiais', [])
            if materiais:
                for mat in materiais:
                    self.rat_materiais_model.create({
                        'rat_id': rat_id,
                        'codigo_engesep': mat.get('codigo'),
                        'descricao': mat['descricao'],
                        'fabricante': mat.get('fabricante'),
                        'quantidade': mat.get('quantidade', 1),
                        'unidade': mat.get('unidade', 'UN')
                    })

            # 4. Fotos - Remoção
            ids_removidos = data.get('ids_fotos_removidas', [])
            if ids_removidos:
                ids_str = ','.join(map(str, ids_removidos))
                
                # Delete files from disk first
                paths = self.rat_fotos_model.read(['caminho_arquivo'], where=f"id IN ({ids_str})")
                for p in paths:
                    try:
                        full_path = p['caminho_arquivo'].lstrip('/') # Remove leading /
                        if full_path.startswith('assets'): # Check relative path
                             full_path = os.path.join(os.getcwd(), full_path)
                        
                        if os.path.exists(full_path):
                            os.remove(full_path)
                    except Exception as ex:
                        print(f"Erro ao deletar arquivo físico: {ex}")

                self.rat_fotos_model.delete(where=f"id IN ({ids_str})")

            # 5. Fotos - Atualizar Legendas Existentes
            fotos_existentes = data.get('fotos_existentes', [])
            for foto in fotos_existentes:
                self.rat_fotos_model.update(
                    {'legenda': foto['legenda']},
                    where=f"id = {foto['id']}"
                )

            # 6. Fotos - Adicionar Novas (Base64)
            novas_fotos = data.get('novas_fotos', [])
            if novas_fotos:
                rat_info = self.rat_model.read(['protocolo'], where=f"id={rat_id}")
                protocolo = rat_info[0]['protocolo'] if rat_info else f"rat_{rat_id}"
                
                for idx, foto in enumerate(novas_fotos):
                    b64 = foto['conteudo']
                    legenda = foto['legenda']
                    if b64 and "base64," in b64:
                         suffix = f"edit_{datetime.now().strftime('%H%M%S')}_{idx}"
                         filename = f"foto_{protocolo}_{suffix}.png"
                         
                         db_path = self.save_base64_image(b64, 'imgs', filename)
                         
                         if db_path:
                            self.rat_fotos_model.create({
                                'rat_id': rat_id,
                                'caminho_arquivo': db_path,
                                'legenda': legenda,
                                'ordem': 0
                            })

            return {'message': 'Atualizado com sucesso'}, 200

        except Exception as e:
            print(f"Erro ao atualizar RAT: {e}")
            return {'message': f'Erro: {str(e)}'}, 500

    def atualizar_status_financeiro(self):
        try:
            data = request.json
            rat_id = data.get('rat_id')
            novo_status = data.get('novo_status')

            if not rat_id or not novo_status:
                return {'message': 'Dados incompletos'}, 400

            # Validar status permitido (opcional, mas bom pra segurança, embora ENUM no banco já segure)
            status_permitidos = ['nao_faturavel', 'pendente_faturamento', 'aguardando_pagamento', 'liquidado', 'inadimplente']
            if novo_status not in status_permitidos:
                return {'message': 'Status inválido'}, 400

            sucesso = self.rat_model.update(
                {'status_financeiro': novo_status},
                where=f"id = {rat_id}"
            )

            if sucesso:
                return {'message': 'Status atualizado com sucesso'}, 200
            else:
                return {'message': 'Erro ao atualizar status'}, 500

        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            return {'message': f'Erro: {str(e)}'}, 500

    def deletar_rat(self):
        try:
            data = request.json
            rat_id = data.get('rat_id')
            password = data.get('password')

            if not rat_id:
                return {'message': 'ID do RAT não fornecido'}, 400
            
            # Simple password check
            if str(password) != "1234":
                return {'message': 'Senha incorreta'}, 401

            # 1. Delete Photos Files from Disk
            fotos = self.rat_fotos_model.read(['caminho_arquivo'], where=f"rat_id = {rat_id}")
            for photo in fotos:
                try:
                    caminho = photo['caminho_arquivo']
                    full_path = caminho.lstrip('/')
                    if full_path.startswith('assets'):
                        full_path = os.path.join(os.getcwd(), full_path)
                    
                    if os.path.exists(full_path):
                        os.remove(full_path)
                except Exception as ex:
                    print(f"Erro ao deletar arquivo fisico durante exclusão do RAT: {ex}")

            # 2. Delete Signatures if exist
            rat = self.rat_model.read(['caminho_assinatura_tec', 'caminho_assinatura_cli'], where=f"id = {rat_id}")
            if rat:
                rat_data = rat[0]
                for key in ['caminho_assinatura_tec', 'caminho_assinatura_cli']:
                    if rat_data.get(key):
                        try:
                            path = rat_data[key].lstrip('/')
                            if path.startswith('assets'):
                                full_path = os.path.join(os.getcwd(), path)
                                if os.path.exists(full_path):
                                    os.remove(full_path)
                        except Exception as sig_ex:
                             print(f"Erro ao deletar assinatura: {sig_ex}")

            # 3. Delete Data from DB (Order matters if constraints exist, though BaseCrud might not enforce cascade automatically depending on DB setup)
            self.rat_fotos_model.delete(where=f"rat_id = {rat_id}")
            self.rat_servicos_model.delete(where=f"rat_id = {rat_id}")
            self.rat_materiais_model.delete(where=f"rat_id = {rat_id}")
            
            # Finally delete the RAT
            self.rat_model.delete(where=f"id = {rat_id}")

            return {'message': 'RAT excluído com sucesso'}, 200

        except Exception as e:
            print(f"Erro ao deletar RAT: {e}")
            return {'message': f'Erro: {str(e)}'}, 500

    def gerar_pdf(self, rat_id):
        try:
            

            mode = request.args.get('mode', 'preview') # preview or download
            
            # 1. Buscar Dados (Reutilizar ver_rat logic logicamente, mas construindo ditos)
            rat_data_resp, status = self.ver_rat(rat_id)
            if status != 200:
                return rat_data_resp, status
            
            data = rat_data_resp
            rat = data['rat']
            servicos = data['servicos']
            materiais = data['materiais']
            fotos = data['fotos']
            
            # Helper para caminho absoluto
            def get_abs_path(rel_path):
                if not rel_path: return ""
                if rel_path.startswith('/'): rel_path = rel_path[1:]
                # Resolve based on project root (assuming ControllerRat is in libs/controllers/)
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                full_path = os.path.join(project_root, rel_path)
                return f"file://{full_path}"

            # Enriquecer dados com caminhos absolutos, formatar datas e calcular horas
            rat['data_emissao_formatada'] = format_date_br(rat.get('data_emissao', ''))
            
            total_seconds_rat = 0
            
            for svc in servicos:
                svc['data_servico_formatada'] = format_date_br(svc.get('data_servico', ''))
                
                # Calcular tempo decorrido e totalizar
                h_inicio = svc.get('hora_inicio', '')
                h_fim = svc.get('hora_fim', '')
                
                tempo_decorrido = "-"
                
                if h_inicio and h_fim and ':' in h_inicio and ':' in h_fim:
                    try:
                        # Parse strings HH:MM
                        h1, m1 = map(int, h_inicio.split(':'))
                        h2, m2 = map(int, h_fim.split(':'))
                        
                        start_mins = h1 * 60 + m1
                        end_mins = h2 * 60 + m2
                        
                        diff_mins = end_mins - start_mins
                        if diff_mins < 0:
                             # Assumindo que pode virar o dia? (improvável em RAT simples,, mas tratar como 24h?)
                             # Por enquanto, assumir mesmo dia. Se negativo, talvez erro de input.
                             diff_mins = 0
                        
                        total_seconds_rat += diff_mins * 60
                        
                        # Formatar HH:MM
                        dh = diff_mins // 60
                        dm = diff_mins % 60
                        tempo_decorrido = f"{dh:02d}:{dm:02d}"
                        
                    except Exception as e:
                        print(f"Erro calculo horas: {e}")
                
                svc['tempo_decorrido'] = tempo_decorrido

            # Atualizar total de horas no objeto RAT
            total_hours_float = total_seconds_rat / 3600
            rat['total_horas'] = format_float_hours(total_hours_float)

            # Tentar resolver caminho do logo de múltiplas formas para robustez
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'logo.png'),
                os.path.join(os.getcwd(), 'assets', 'logo.png'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'logo.webp'),
                os.path.join(os.getcwd(), 'assets', 'logo.webp')
            ]
            
            logo_path = ""
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = f"file://{path}"
                    break

            # Assinaturas
            rat['caminho_assinatura_tec_absoluto'] = get_abs_path(rat.get('caminho_assinatura_tec'))
            rat['caminho_assinatura_cli_absoluto'] = get_abs_path(rat.get('caminho_assinatura_cli'))

            # Fotos
            for foto in fotos:
                foto['caminho_absoluto'] = get_abs_path(foto.get('caminho_arquivo'))

            html = render_template(
                'components/_pdf_rats.html',
                rat=rat,
                servicos=servicos,
                materiais=materiais,
                fotos=fotos,
                logo_path=logo_path
            )

            pdf_bytes = gerar_pdf_bytes(html)
            
            response = make_response(pdf_bytes)
            response.headers['Content-Type'] = 'application/pdf'
            
            filename = f"RAT_{rat['protocolo']}.pdf"
            
            if mode == 'download':
                response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            else:
                response.headers['Content-Disposition'] = f'inline; filename={filename}'
            
            return response

        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return {'message': f'Erro ao gerar PDF: {str(e)}'}, 500

# Views

{% extends "base.html" %}
{% set active_page = "home" %}
{% import "components/_cards.html" as cards %}
{% from "components/macros.html" import ocorrencia_item %}

{% block title %}Dashboard de Ocorrências — EngeSEP O&M{% endblock %}

{% block content %}
<main class="flex-1 flex flex-col h-full overflow-hidden relative">
    <div class="flex-shrink-0 bg-[var(--color-bg)] border-b border-slate-200 dark:border-slate-800 z-10 pt-6">
        <div class="px-6 max-w-6xl mx-auto w-full">
            <nav aria-label="Tabs" class="flex gap-6">
                <!-- Tab: Informações -->
                <a href="/rats" class="group inline-flex items-center pb-3 px-1 border-b-2 font-medium text-sm transition
                            {% if page == 'inforat' %}
                                border-primary text-primary
                            {% else %}
                                border-transparent text-text-muted hover:text-text-primary hover:border-slate-300
                            {% endif %}">
                    <span
                        class="material-icons mr-1 text-base align-middle {% if page == 'inforat' %} text-primary {% endif %}">info</span>
                    Informações
                </a>

                <!-- Tab: Criar RAT -->
                <a href="/criarrat" class="group inline-flex items-center pb-3 px-1 border-b-2 font-medium text-sm transition
                            {% if page == 'criarrat' %}
                                border-primary text-primary
                            {% else %}
                                border-transparent text-text-muted hover:text-text-primary hover:border-slate-300
                            {% endif %}">
                    <span
                        class="material-icons mr-1 text-base align-middle {% if page == 'criarrat' %} text-primary {% endif %}">add_circle</span>
                    Criar RAT
                </a>

                <!-- Tab: Modificar -->
                <a href="/modificarrat" class="group inline-flex items-center pb-3 px-1 border-b-2 font-medium text-sm transition
                            {% if page == 'modificarrat' %}
                                border-primary text-primary
                            {% else %}
                                border-transparent text-text-muted hover:text-text-primary hover:border-slate-300
                            {% endif %}">
                    <span
                        class="material-icons mr-1 text-base align-middle {% if page == 'modificarrat' %} text-primary {% endif %}">edit</span>
                    Modificar
                </a>
            </nav>
        </div>
    </div>

    <!-- Dynamic Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar relative">
        {% if page == 'inforat' %}
        {% include 'components/_info_rats.html' %}
        {% elif page == 'criarrat' %}
        {% include 'components/_criar_rats.html' %}
        {% elif page == 'modificarrat' %}
        {% include 'components/_modificar_rats.html' %}
        {% endif %}
    </div>
    {% include 'components/_alert.html' %}
</main>
</div>
{% endblock %}

<!-- Tailwind Config removed to use standard variables -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
    .custom-scrollbar::-webkit-scrollbar {
        height: 8px;
        width: 8px;
    }

    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb {
        background-color: #475569;
        border-radius: 4px;
    }
</style>

<!-- Main Content Area (Sidebar Removed) -->
<div
    class="flex flex-col w-full min-h-screen bg-[var(--color-bg)] text-[var(--color-text)] font-sans antialiased transition-colors duration-200">
    <!-- Content Scrollable Area -->
    <div class="p-6 space-y-6">
        <!-- <div class="flex-1 p-4 md:p-6 lg:p-8"> -->

        {% import 'components/_cards.html' as cards %}

        <!-- KPI Cards -->
        {% set cads_kpis = [
        {
        'title': 'Total RATs (' ~ current_month ~ ')',
        'value': kpis.total_rats_month
        },
        {
        'title': 'Horas Totais',
        'value': kpis.total_hours_month,
        'unit': 'h',
        'description': 'Acumulado em ' ~ current_month
        },
        {
        'title': 'Usina com mais Horas',
        'value': kpis.top_plant.obra_nome if kpis.top_plant else '-',
        'description': (kpis.top_plant.total_hours|round(1) if kpis.top_plant else 0) ~ 'h trabalhadas'
        },
        {
        'title': 'Tempo Médio',
        'value': kpis.avg_time_str,
        'description': 'Por RAT finalizada'
        },
        {
        'title': 'Pendência Assinatura',
        'value': kpis.pending_signatures,
        'description': 'Requer atenção imediata',
        'text_color_class': 'text-red-600 dark:text-red-400',
        'extra_classes': 'border-red-200 dark:border-red-900/50 shadow-sm relative overflow-hidden group'
        }
        ] %}

        <div class="cards-rats">
            {% for card_data in cads_kpis %}
            {{ cards.card(
            title=card_data.title,
            value=card_data.value,
            unit=card_data.unit,
            description=card_data.description,
            text_color_class=card_data.text_color_class,
            extra_classes=card_data.extra_classes
            ) }}
            {% endfor %}
        </div>

        <!-- Main Layout Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">

            <!-- Left Column: Charts & Lists -->
            <div class="lg:col-span-1 flex flex-col gap-6">
                <!-- Priority Chart -->
                <div style="background-color: var(--color-surface);"
                    class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center">
                    <h3 class="text-sm font-semibold text-[var(--color-text)] mb-2 w-full text-left">Distribuição por
                        Prioridade
                    </h3>
                    <div class="relative h-40 w-40">
                        <canvas id="priorityChart"></canvas>
                    </div>
                    <div class="mt-2 flex justify-center gap-4 text-xs">
                        <div class="flex items-center gap-1">
                            <span class="w-2 h-2 rounded-full bg-red-500"></span>
                            <span class="text-[var(--color-text-muted)]">Alta</span>
                        </div>
                        <div class="flex items-center gap-1">
                            <span class="w-2 h-2 rounded-full bg-yellow-500"></span>
                            <span class="text-[var(--color-text-muted)]">Baixa</span>
                        </div>
                    </div>
                </div>

                <!-- Tech Hours Chart -->
                <div style="background-color: var(--color-surface);"
                    class="p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
                    <h3 class="text-sm font-semibold text-[var(--color-text)] mb-4">Horas por Técnico</h3>
                    <div class="flex-1 min-h-[100px] max-h-[120px] relative">
                        <canvas id="techHoursChart"></canvas>
                    </div>
                </div>

                <!-- Top Clients -->
                <div style="background-color: var(--color-surface);"
                    class="p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm h-fit">
                    <h3 class="text-sm font-semibold text-[var(--color-text)] mb-6">Top 5 Clientes Recorrentes
                    </h3>
                    <div class="space-y-5">
                        {% for client in top_clients %}
                        <div>
                            <div class="flex justify-between text-xs mb-1">
                                <span class="text-[var(--color-text-muted)]">{{ client.obra_nome }}</span>
                                <span class="text-[var(--color-text-muted)] font-medium">{{ client.count }}
                                    RATs</span>
                            </div>
                            <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1.5">
                                <div class="{{ ['bg-primary', 'bg-cyan-500', 'bg-indigo-500', 'bg-violet-500', 'bg-fuchsia-500'][loop.index0 % 5] }} h-1.5 rounded-full"
                                    style="width: {{ client.percentage }}%"></div>
                            </div>
                        </div>
                        {% else %}
                        <p class="text-xs text-[var(--color-text-muted)]">Nenhum dado disponível.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Right Column: Table -->
            {% include 'components/_tabela_rats.html' %}
        </div>

    </div>
</div>

<script>
    async function changePage(e) {
        e.preventDefault();
        const btn = e.currentTarget;
        const page = btn.getAttribute('data-page');
        if (!page || page < 1) return;

        try {
            // Add loading state opacity
            const container = document.getElementById('rat-table-container');
            container.style.opacity = '0.5';
            container.style.pointerEvents = 'none';

            const response = await fetch(`/rats?page=${page}&partial=true`);
            if (response.ok) {
                const html = await response.text();
                // Create a temporary container to extract the new content
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;

                // If the response is the full table container, replace the current one
                // The partial returns the root element <div id="rat-table-container">...</div>
                // So we replace the current container with the new one
                if (tempDiv.firstElementChild) {
                    container.replaceWith(tempDiv.firstElementChild);
                }
            } else {
                console.error('Failed to load page');
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            // Restore opacity in case of error
            const container = document.getElementById('rat-table-container');
            if (container) {
                container.style.opacity = '1';
                container.style.pointerEvents = 'auto';
            }
        }
    }

    // Initialize Charts with dynamic data
    const chartData = JSON.parse('{{ charts | safe }}');

    // Priority Donut Chart
    const priorityCtx = document.getElementById('priorityChart').getContext('2d');
    new Chart(priorityCtx, {
        type: 'doughnut',
        data: {
            labels: chartData.priority.labels,
            datasets: [{
                data: chartData.priority.data,
                backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            cutout: '70%',
        }
    });

    // Tech Hours Vertical Bar Chart
    const techHoursCtx = document.getElementById('techHoursChart').getContext('2d');
    new Chart(techHoursCtx, {
        type: 'bar',
        data: {
            labels: chartData.tech_hours.labels,
            datasets: [{
                label: 'Horas',
                data: chartData.tech_hours.data,
                backgroundColor: '#6366f1',
                borderRadius: 3,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { beginAtZero: true, grid: { color: 'rgba(148, 163, 184, 0.1)' }, ticks: { color: '#94a3b8' } },
                y: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            },
            plugins: { legend: { display: false } }
        }
    });
</script>

<div class="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth">
    <div class="max-w-6xl mx-auto w-full space-y-6 pb-24">
        <section
            class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <div
                class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center dark:bg-slate-800/50">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-primary">domain</span>
                    <h3 class="rat-text-primary text-lg font-bold">Cliente &amp; Obra</h3>
                </div>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Cliente</span>
                    <div class="relative">
                        <select id="select-cliente" onchange="atualizarDadosCliente()"
                            class="rat-input rat-select cursor-pointer">
                            <option value="" selected disabled>Selecione um cliente...</option>
                            {% for cliente in clientes %}
                            <option value="{{ cliente.id }}">{{ cliente.nome_razao }}</option>
                            {% endfor %}
                        </select>

                    </div>
                </label>
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Obra / Usina</span>
                    <div class="relative">
                        <select id="select-obra" class="rat-input rat-select cursor-pointer">
                            <option value="" selected disabled>Selecione a obra...</option>
                        </select>

                    </div>
                </label>
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Cidade / UF</span>
                    <input id="input-cidade" class="rat-input cursor-not-allowed" readonly="" type="text" value="" />
                </label>
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">CNPJ</span>
                    <input id="input-cnpj" class="rat-input cursor-not-allowed" readonly="" type="text" value="" />
                </label>
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Protocolo</span>
                    <input class="rat-input cursor-not-allowed" readonly="" type="text" value="{{ protocolo }}" />
                </label>
            </div>
        </section>
        <section
            class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2">
                <span class="material-symbols-outlined text-primary">assignment</span>
                <h3 class="rat-text-primary text-lg font-bold">Resumo do Chamado</h3>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Data da Solicitação</span>
                    <input class="rat-input dark:[color-scheme:dark]" type="date" value="{{ data_atual }}" />
                </label>
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Solicitante</span>
                    <input class="rat-input placeholder:text-gray-600" placeholder="Nome do contato" type="text" />
                </label>
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Tipo de Atividade</span>
                    <div class="relative">
                        <select id="select-atividade" class="rat-input rat-select cursor-pointer">
                            <option>Manutenção Preventiva</option>
                            <option>Manutenção Corretiva</option>
                            <option>Instalação</option>
                            <option>Consultoria</option>
                        </select>

                    </div>
                </label>
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Prioridade</span>
                    <div class="relative">
                        <select id="select-prioridade" class="rat-input rat-select cursor-pointer">
                            <option>Alta</option>
                            <option>Média</option>
                            <option>Baixa</option>
                        </select>

                    </div>
                </label>
                <div class="md:col-span-2 lg:col-span-4 flex items-center gap-4 py-2">
                    <span class="text-sm font-medium rat-text-muted">Equipamento em Garantia?</span>
                    <label class="inline-flex items-center cursor-pointer">
                        <input id="input-garantia" class="sr-only peer" type="checkbox" value="" />
                        <div
                            class="relative w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary">
                        </div>
                        <span class="ms-3 text-sm font-medium text-white">Sim</span>
                    </label>
                </div>
                <label class="md:col-span-2 lg:col-span-4 flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Relato do Cliente (Defeito
                        Reclamado)</span>
                    <textarea id="txt-relato" class="rat-input resize-none placeholder-slate-400"
                        placeholder="Descreva brevemente o problema relatado pelo cliente..." rows="3"></textarea>
                </label>
            </div>
        </section>
        <section
            class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-primary">schedule</span>
                    <h3 class="rat-text-primary text-lg font-bold">Horas de Serviço</h3>
                </div>
                <button id="btn-adicionar-horas"
                    class="text-xs font-bold text-primary hover:text-white bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">
                    <span class="material-symbols-outlined text-sm">add</span> Adicionar Horas
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                            <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                Data</th>
                            <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                Hora Início</th>
                            <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                Hora Fim</th>
                            <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                Executante</th>
                            <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider w-1/3">
                                Observações</th>
                            <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider w-10">
                            </th>
                        </tr>
                    </thead>
                    <tbody id="tbody-horas" class="divide-y divide-slate-200 dark:divide-slate-800">
                        <tr class="group hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors">
                            <td class="p-3"><input class="rat-input text-sm input-data" type="date" /></td>
                            <td class="p-3"><input class="rat-input text-sm input-hora-inicio" type="time"
                                    onchange="calcularTotalHoras()" /></td>
                            <td class="p-3"><input class="rat-input text-sm input-hora-fim" type="time"
                                    onchange="calcularTotalHoras()" /></td>
                            <td class="p-3">
                                <select class="rat-input rat-select text-sm input-executante">
                                    <option value="" selected disabled>Selecione...</option>
                                    {% for usuario in usuarios %}
                                    <option value="{{ usuario.id }}">{{ usuario.nome }}</option>
                                    {% endfor %}
                                </select>
                            </td>
                            <td class="p-3"><input class="rat-input text-sm" placeholder="Notas" type="text" /></td>
                            <td class="p-3 text-center">
                                <button class="rat-text-muted hover:text-red-500 transition-colors"
                                    onclick="removerLinhaHoras(this)">
                                    <span class="material-symbols-outlined text-lg">delete</span>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div
                class="p-4 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 flex justify-between items-center">
                <div class="flex items-center gap-2 w-1/3">
                    <span class="text-sm font-medium rat-text-muted">Deslocamento:</span>
                    <input id="input-deslocamento" type="text" class="rat-input text-sm h-9 px-3"
                        placeholder="Ex: 150km ou Remoto">
                </div>
                <p class="text-sm rat-text-muted">Total de Horas: <span id="total-horas"
                        class="rat-text-primary font-bold">00:00</span>
                </p>
            </div>
        </section>
        <section
            class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-visible shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-primary">inventory_2</span>
                    <h3 class="rat-text-primary text-lg font-bold">Materiais Utilizados</h3>
                </div>
                <button id="btn-adicionar-material"
                    class="text-xs font-bold text-primary hover:text-white bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">
                    <span class="material-symbols-outlined text-sm">add</span> Adicionar Material
                </button>
            </div>
            <div class="overflow-visible">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <thead>
                            <tr class="dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider w-24">
                                    Cód.</th>
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                    Descrição</th>
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                    Fabricante</th>
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider w-20">
                                    Qtd</th>
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider w-24">
                                    Unidade</th>
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider w-10">
                                </th>
                            </tr>
                        </thead>
                    <tbody id="tbody-materiais" class="divide-y divide-slate-200 dark:divide-slate-800">
                        <tr class="group hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors relative">
                            <td class="p-3"><input class="rat-input text-sm input-codigo" placeholder="SKU" type="text"
                                    readonly /></td>
                            <td class="p-3 relative">
                                <input class="rat-input text-sm input-descricao" placeholder="Buscar produto..."
                                    type="text" autocomplete="off" oninput="buscarProduto(this)" />
                                <div
                                    class="absolute top-11 left-0 right-0 rat-bg-surface border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 hidden results-container max-h-60 overflow-y-auto">
                                    <!-- Results go here -->
                                </div>
                            </td>
                            <td class="p-3"><input class="rat-input text-sm input-fabricante" placeholder="Marca"
                                    type="text" readonly /></td>
                            <td class="p-3"><input class="rat-input text-sm text-center input-qtd" type="number"
                                    value="1" step="0.01" /></td>
                            <td class="p-3">
                                <input class="rat-input text-sm input-unidade" type="text" readonly />
                            </td>
                            <td class="p-3 text-center">
                                <button class="rat-text-muted hover:text-red-500 transition-colors"
                                    onclick="removerLinhaMaterial(this)">
                                    <span class="material-symbols-outlined text-lg">delete</span>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
        <section
            class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-primary">article</span>
                    <h3 class="rat-text-primary text-lg font-bold">Relatório Técnico</h3>
                </div>
                <button type="button" onclick="gerarRelatorioIA()" id="btn-ia-gerar"
                    class="text-xs font-bold text-white bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 px-3 py-1.5 rounded-lg transition-all shadow-md flex items-center gap-1 group">
                    <span class="material-symbols-outlined text-sm group-hover:animate-pulse">auto_awesome</span>
                    Preencher com IA
                </button>
            </div>
            <div class="p-6 grid grid-cols-1 gap-6">
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Descrição das Atividades
                        Realizadas</span>
                    <textarea id="txt-descricao"
                        class="w-full rat-input rounded-xl p-4 focus:ring-2 focus:ring-primary resize-none placeholder:text-gray-600"
                        placeholder="Detalhamento técnico do serviço executado, medições, testes, etc..."
                        rows="6"></textarea>
                </label>
                <label class="flex flex-col gap-2">
                    <span class="text-sm font-medium rat-text-muted">Conclusão e Pendências</span>
                    <textarea id="txt-conclusao" class="rat-input resize-none placeholder:text-gray-600"
                        placeholder="Equipamento liberado? Restou alguma pendência?" rows="4"></textarea>
                </label>
            </div>
        </section>
        <!-- Fotos & Assinaturas -->
        <section
            class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2">
                <span class="material-symbols-outlined text-primary">draw</span>
                <h3 class="rat-text-primary text-lg font-bold">Fotos & Assinaturas</h3>
            </div>

            <div class="p-6 space-y-8">
                <!-- Evidências Fotográficas (Drag & Drop) -->
                <div>
                    <h4 class="text-sm font-medium rat-text-muted mb-2">Evidências Fotográficas</h4>

                    <div id="drop-area"
                        class="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl rat-bg-main h-48 flex flex-col items-center justify-center transition-colors cursor-pointer hover:border-primary hover:bg-slate-100 dark:hover:bg-slate-800"
                        onclick="document.getElementById('input-foto').click()"
                        ondragover="event.preventDefault(); this.classList.add('border-primary', 'bg-slate-100', 'dark:bg-slate-800')"
                        ondragleave="this.classList.remove('border-primary', 'bg-slate-100', 'dark:bg-slate-800')"
                        ondrop="handleDrop(event)">
                        <span class="material-symbols-outlined text-4xl rat-text-muted mb-3">cloud_upload</span>
                        <p class="text-sm text-primary font-bold">Clique para enviar <span
                                class="rat-text-muted font-normal">ou arraste e solte</span></p>
                        <p class="text-xs rat-text-muted mt-1">PNG, JPG até 10MB</p>
                        <input type="file" id="input-foto" accept="image/*" class="hidden" onchange="uploadFoto(this)">
                    </div>

                    <!-- Grid de Fotos Pré-visualizadas -->
                    <div id="grid-fotos" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mt-4">
                        <!-- Fotos adicionadas aparecerão aqui via JS -->
                    </div>
                </div>

                <!-- Assinaturas -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div class="flex flex-col gap-2">
                        <span class="text-sm font-medium rat-text-muted">Assinatura do Técnico</span>
                        <div class="bg-white rounded-xl h-40 w-full relative group shadow-inner overflow-hidden">
                            <canvas id="canvas-tecnico" class="w-full h-full cursor-crosshair touch-none"></canvas>
                            <div class="absolute inset-0 flex items-center justify-center pointer-events-none"
                                id="placeholder-tecnico">
                                <p class="text-gray-300 text-sm font-medium select-none">Assine aqui</p>
                            </div>
                            <button type="button" onclick="limparAssinatura('tecnico')"
                                class="absolute top-2 right-2 text-gray-400 hover:text-red-500 bg-gray-100 rounded p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                title="Limpar">
                                <span class="material-symbols-outlined text-sm">close</span>
                            </button>
                            <div class="absolute bottom-8 left-4 right-4 border-b border-gray-300 pointer-events-none">
                            </div>
                        </div>
                        <input id="nome-tecnico" class="rat-input text-sm mt-1" placeholder="Nome Legível do Técnico"
                            type="text" />
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="text-sm font-medium rat-text-muted">Assinatura do Cliente</span>
                        <div class="bg-white rounded-xl h-40 w-full relative group shadow-inner overflow-hidden">
                            <canvas id="canvas-cliente" class="w-full h-full cursor-crosshair touch-none"></canvas>
                            <div class="absolute inset-0 flex items-center justify-center pointer-events-none"
                                id="placeholder-cliente">
                                <p class="text-gray-300 text-sm font-medium select-none">Assine aqui</p>
                            </div>
                            <button type="button" onclick="limparAssinatura('cliente')"
                                class="absolute top-2 right-2 text-gray-400 hover:text-red-500 bg-gray-100 rounded p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                title="Limpar">
                                <span class="material-symbols-outlined text-sm">close</span>
                            </button>
                            <div class="absolute bottom-8 left-4 right-4 border-b border-gray-300 pointer-events-none">
                            </div>
                        </div>
                        <input id="nome-cliente" class="rat-input text-sm mt-1" placeholder="Nome Legível do Cliente"
                            type="text" />
                    </div>
                </div>

            </div>
        </section>
    </div>
</div>
<div class="flex-shrink-0 rat-bg-surface border-t border-slate-200 dark:border-slate-800 p-4 lg:px-8 shadow-2xl z-20">
    <div class="max-w-6xl mx-auto flex items-center justify-between">
        <button
            class="h-12 px-6 rounded-xl rat-text-muted font-bold hover:rat-text-primary hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            onclick="document.location.href = '/rats'">
            Cancelar
        </button>
        <div class="flex gap-4">
            <button
                class="h-12 px-8 rounded-xl bg-primary text-white font-bold hover:bg-blue-600 transition-colors shadow-[0_0_15px_rgba(19,127,236,0.3)] flex items-center gap-2">
                <span class="material-symbols-outlined">check_circle</span>
                Salvar
            </button>
        </div>
    </div>
</div>

<script>
    // Recebe os dados do Python convertidos para JSON
    const dadosClientes = {{ clientes_json | safe }};

    function atualizarDadosCliente() {
        const select = document.getElementById('select-cliente');
        const clienteId = parseInt(select.value);

        // Encontra o cliente selecionado na lista
        const cliente = dadosClientes.find(c => c.id === clienteId);

        if (cliente) {
            // Preenche CNPJ e Cidade
            document.getElementById('input-cnpj').value = cliente.cnpj || '';
            document.getElementById('input-cidade').value = cliente.cidade || '';

            // Atualiza o Select de Obras
            const selectObra = document.getElementById('select-obra');
            selectObra.innerHTML = '<option value="" selected disabled>Selecione a obra...</option>';

            if (cliente.obras) {
                // Assume que obras podem vir separadas por vírgula se for string, 
                // ou ajustamos conforme seu banco. Se for só uma string:
                const obra = cliente.obras;
                // Cria a option
                const option = document.createElement('option');
                option.value = obra;
                option.text = obra;
                option.selected = true; // Já seleciona se for única
                selectObra.appendChild(option);
            }
        }
    }
</script>
<script>
    // Script e Lógica para Horas de Serviço
    document.getElementById('btn-adicionar-horas').addEventListener('click', function () {
        const tbody = document.getElementById('tbody-horas');
        // Clona a primeira linha para manter o estilo
        const novaLinha = tbody.rows[0].cloneNode(true);

        // Limpa os valores dos inputs e selects
        const inputs = novaLinha.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.value = '';
            // Reatribui o evento onchange, embora o cloneNode já deva trazer se in-line, 
            // mas é bom garantir ou se usarmos addEventListener no futuro.
            // Aqui como está inline no HTML (onchange="..."), o clone funciona.
        });

        tbody.appendChild(novaLinha);
    });

    function removerLinhaHoras(btn) {
        const row = btn.closest('tr');
        const tbody = document.getElementById('tbody-horas');

        // Impede remover a última linha restante
        if (tbody.rows.length > 1) {
            row.remove();
            calcularTotalHoras();
        } else {
            // Se for a única linha, apenas limpa os valores
            const inputs = row.querySelectorAll('input');
            inputs.forEach(input => input.value = '');
            calcularTotalHoras();
        }
    }

    function calcularTotalHoras() {
        const tbody = document.getElementById('tbody-horas');
        let totalMinutos = 0;

        for (let i = 0; i < tbody.rows.length; i++) {
            const row = tbody.rows[i];
            const inicio = row.querySelector('.input-hora-inicio').value;
            const fim = row.querySelector('.input-hora-fim').value;

            if (inicio && fim) {
                const [hInicio, mInicio] = inicio.split(':').map(Number);
                const [hFim, mFim] = fim.split(':').map(Number);

                const minutosInicio = hInicio * 60 + mInicio;
                const minutosFim = hFim * 60 + mFim;

                let diferenca = minutosFim - minutosInicio;

                // Se o horário final for menor que o inicial, assume que passou da meia-noite
                // (Opcional: Descomentar se quiser essa lógica)
                // if (diferenca < 0) {
                //    diferenca += 24 * 60;
                // }

                // Se diferenca for positiva (ou tratada), soma
                if (diferenca > 0) {
                    totalMinutos += diferenca;
                }
            }
        }

        const horasTotal = Math.floor(totalMinutos / 60);
        const minutosTotal = totalMinutos % 60;

        const textoTotal = `${String(horasTotal).padStart(2, '0')}:${String(minutosTotal).padStart(2, '0')}`;
        document.getElementById('total-horas').innerText = textoTotal;
    }

    // Script e Lógica para Materiais Utilizados
    document.getElementById('btn-adicionar-material').addEventListener('click', function () {
        const tbody = document.getElementById('tbody-materiais');
        // Clona a primeira linha para manter o estilo
        const novaLinha = tbody.rows[0].cloneNode(true);

        const inputs = novaLinha.querySelectorAll('input');
        inputs.forEach(input => {
            if (input.type === 'number') {
                input.value = '1';
            } else {
                input.value = '';
            }
        });

        // Limpar lista de resultados clonada
        const resultsContainer = novaLinha.querySelector('.results-container');
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
            resultsContainer.classList.add('hidden');
        }

        tbody.appendChild(novaLinha);
    });

    function removerLinhaMaterial(btn) {
        const row = btn.closest('tr');
        const tbody = document.getElementById('tbody-materiais');

        if (tbody.rows.length > 1) {
            row.remove();
        } else {
            const inputs = row.querySelectorAll('input');
            inputs.forEach(input => {
                if (input.type === 'number') {
                    input.value = '1';
                } else {
                    input.value = '';
                }
            });
        }
    }

    let searchTimeout = null;

    async function buscarProduto(input) {
        const tr = input.closest('tr');
        const resultsDiv = tr.querySelector('.results-container');
        const query = input.value;

        if (query.length < 2) {
            resultsDiv.classList.add('hidden');
            return;
        }

        // Debounce
        if (searchTimeout) clearTimeout(searchTimeout);

        searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/produtos/buscar?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                resultsDiv.innerHTML = '';
                if (data.results && data.results.length > 0) {
                    data.results.forEach(prod => {
                        const div = document.createElement('div');
                        div.className = "px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer text-sm rat-text-primary";
                        div.innerHTML = `
                            <div class="font-bold rat-text-primary">${prod.codigo_produto}</div>
                            <div class="text-xs rat-text-muted">${prod.descricao}</div>
                            <div class="text-[10px] text-gray-500">${prod.marca || ''}</div>
                        `;
                        div.onclick = () => selecionarProduto(tr, prod);
                        resultsDiv.appendChild(div);
                    });
                    resultsDiv.classList.remove('hidden');
                } else {
                    resultsDiv.innerHTML = '<div class="px-3 py-2 text-xs text-gray-500">Nenhum produto encontrado.</div>';
                    resultsDiv.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Erro ao buscar produtos:', error);
            }
        }, 300);
    }

    function selecionarProduto(tr, produto) {
        tr.querySelector('.input-codigo').value = produto.codigo_produto || '';
        tr.querySelector('.input-descricao').value = produto.descricao || '';
        tr.querySelector('.input-fabricante').value = produto.marca || '';
        tr.querySelector('.input-unidade').value = produto.unidade || 'UN';

        tr.querySelector('.results-container').classList.add('hidden');
    }

    // Fechar resultados ao clicar fora
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.results-container') && !e.target.closest('.input-descricao')) {
            document.querySelectorAll('.results-container').forEach(el => el.classList.add('hidden'));
        }
    });

    // Funcionalidade de Salvar RAT


    // Lógica para Fotos (Drag & Drop Atualizada)
    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();

        const dropArea = document.getElementById('drop-area');
        dropArea.classList.remove('border-primary', 'bg-[#181d23]');

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            // Processa apenas o primeiro arquivo por enquanto ou pode adaptar para multiplos
            const input = document.getElementById('input-foto');
            input.files = e.dataTransfer.files;
            uploadFoto(input);
        }
    }

    async function uploadFoto(input) {
        if (input.files && input.files[0]) {
            const file = input.files[0];
            const formData = new FormData();
            formData.append('file', file);

            // Feedback simples
            const dropArea = document.getElementById('drop-area');
            const originalText = dropArea.innerHTML;
            dropArea.innerHTML = '<span class="material-symbols-outlined text-4xl animate-spin text-primary">progress_activity</span>';

            try {
                const response = await fetch('/rat/upload_foto', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    adicionarCardFoto(result.url, file.name);
                } else {
                    customAlert('Erro', 'Erro ao enviar foto: ' + result.message, 'error');
                }
            } catch (error) {
                console.error('Erro no upload:', error);
                customAlert('Erro', 'Erro ao conectar com o servidor para upload.', 'error');
            } finally {
                input.value = ''; // Limpar input
                dropArea.innerHTML = originalText; // Restaurar texto
            }
        }
    }

    function adicionarCardFoto(url, originalName) {
        // Remover hidden se fosse usado, mas agora não usamos msg-sem-fotos
        const grid = document.getElementById('grid-fotos');

        const div = document.createElement('div');
        div.className = 'foto-item group relative bg-[#181d23] border border-[#283039] rounded-lg overflow-hidden flex flex-col transition-all hover:scale-105';
        div.innerHTML = `
            <div class="relative aspect-video bg-black/50">
                <img src="${url}" class="w-full h-full object-cover" data-path="${url}">
                <button onclick="removerFoto(this)" class="absolute top-1 right-1 bg-red-500/80 hover:bg-red-600 text-white rounded-full p-1 transition-colors shadow-lg opacity-0 group-hover:opacity-100">
                    <span class="material-symbols-outlined text-sm">close</span>
                </button>
            </div>
            <div class="p-2">
                <input type="text" placeholder="Legenda..." class="w-full bg-transparent text-xs text-white placeholder-text-secondary focus:outline-none border-b border-transparent focus:border-primary pb-1 transition-colors">
            </div>
        `;
        grid.appendChild(div);
    }

    function removerFoto(btn) {
        const item = btn.closest('.foto-item');
        item.remove();
        // Não precisamos mais verificar msg-sem-fotos
    }

    // Logic for Signatures
    const signaturePads = {};

    function initSignatureCanvas(canvasId, placeholderId) {
        const canvas = document.getElementById(canvasId);
        const placeholder = document.getElementById(placeholderId);
        const ctx = canvas.getContext('2d');
        let isDrawing = false;

        // Set canvas resolution to match display size
        function resizeCanvas() {
            // Only resize if dimensions changed to avoid clearing content unnecessarily during minor layout shifts
            if (canvas.width !== canvas.offsetWidth || canvas.height !== canvas.offsetHeight) {
                // Note: Resizing clears the canvas. 
                // If we needed to keep content, we'd need to save it and redraw.
                // For now, we accept that resizing window clears signature (common trade-off in simple implementations).
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
                ctx.lineWidth = 2;
                ctx.lineCap = 'round';
                ctx.strokeStyle = '#000000';
            }
        }

        // Initial setup
        resizeCanvas();
        // Debounced resize could be better, but simple listener for now:
        // window.addEventListener('resize', resizeCanvas); 

        function getPos(e) {
            const rect = canvas.getBoundingClientRect();
            // Handle both mouse and touch
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            return {
                x: clientX - rect.left,
                y: clientY - rect.top
            };
        }

        function startDrawing(e) {
            isDrawing = true;
            placeholder.style.display = 'none';
            const pos = getPos(e);
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
            e.preventDefault(); // Prevent scrolling on touch
        }

        function stopDrawing() {
            if (isDrawing) {
                isDrawing = false;
                ctx.closePath();
            }
        }

        function draw(e) {
            if (!isDrawing) return;
            e.preventDefault();
            const pos = getPos(e);
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
        }

        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('mouseout', stopDrawing);

        canvas.addEventListener('touchstart', startDrawing, { passive: false });
        canvas.addEventListener('touchmove', draw, { passive: false });
        canvas.addEventListener('touchend', stopDrawing);

        signaturePads[canvasId] = { canvas, ctx, placeholder };
    }

    function limparAssinatura(tipo) {
        const canvasId = `canvas-${tipo}`;
        const placeholderId = `placeholder-${tipo}`;
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        document.getElementById(placeholderId).style.display = 'flex';
    }

    // Initialize signatures when DOM is ready (already at bottom of body)
    initSignatureCanvas('canvas-tecnico', 'placeholder-tecnico');
    initSignatureCanvas('canvas-cliente', 'placeholder-cliente');

    async function salvarRat() {
        // Coleta de Dados Básicos
        const clienteSelect = document.getElementById('select-cliente');
        const obraSelect = document.getElementById('select-obra');
        const atividadeSelect = document.getElementById('select-atividade');
        const prioridadeSelect = document.getElementById('select-prioridade');

        const protocolo = document.querySelector('input[value="{{ protocolo }}"]').value;
        const dataSolicitacao = document.querySelector('input[type="date"]').value;
        const solicitanteElement = document.getElementById('input-solicitante');
        const solicitante = solicitanteElement ? solicitanteElement.value : document.querySelector('input[placeholder="Nome do contato"]').value;

        const garantiaCheckbox = document.getElementById('input-garantia');
        const emGarantia = garantiaCheckbox ? garantiaCheckbox.checked : false;

        const relatoClienteElement = document.getElementById('txt-relato');
        const relatoCliente = relatoClienteElement ? relatoClienteElement.value : "";

        const descricaoAtividadesElement = document.getElementById('txt-descricao');
        const descricaoAtividades = descricaoAtividadesElement ? descricaoAtividadesElement.value : "";

        const conclusaoElement = document.getElementById('txt-conclusao');
        const conclusao = conclusaoElement ? conclusaoElement.value : "";

        // Validação Básica
        if (!clienteSelect.value || !obraSelect.value) {
            customAlert('Atenção', 'Por favor, selecione o Cliente e a Obra.', 'warning');
            return;
        }

        // Coleta de Horas
        const horas = [];
        const linhasHoras = document.querySelectorAll('#tbody-horas tr');
        linhasHoras.forEach(row => {
            const dataInput = row.querySelector('.input-data');
            const inicioInput = row.querySelector('.input-hora-inicio');
            const fimInput = row.querySelector('.input-hora-fim');
            const executanteInput = row.querySelector('.input-executante');
            const obsInput = row.querySelector('input[placeholder="Notas"]');

            if (dataInput && inicioInput && fimInput && executanteInput) {
                const data = dataInput.value;
                const inicio = inicioInput.value;
                const fim = fimInput.value;
                const executante = executanteInput.value;
                const obs = obsInput ? obsInput.value : "";

                if (data && inicio && fim && executante) {
                    horas.push({
                        data: data,
                        hora_inicio: inicio,
                        hora_fim: fim,
                        executante_id: executante,
                        observacoes: obs
                    });
                }
            }
        });

        // Coleta de Materiais
        const materiais = [];
        const linhasMateriais = document.querySelectorAll('#tbody-materiais tr');
        linhasMateriais.forEach(row => {
            const inputs = row.querySelectorAll('input');

            // Expected inputs order: codigo, descricao, fabricante, qtd, unidade
            if (inputs.length >= 5) {
                const codigo = inputs[0].value;
                const descricao = inputs[1].value;
                const fabricante = inputs[2].value;
                const qtd = inputs[3].value;
                const unidade = inputs[4].value;

                if (descricao && qtd) {
                    materiais.push({
                        codigo: codigo,
                        descricao: descricao,
                        fabricante: fabricante,
                        quantidade: qtd,
                        unidade: unidade
                    });
                }
            }
        });

        // Coleta de Fotos
        const fotos = [];
        const itemsFotos = document.querySelectorAll('.foto-item');
        itemsFotos.forEach(item => {
            const img = item.querySelector('img');
            const legendaInput = item.querySelector('input[type="text"]');

            if (img && img.dataset.path) {
                fotos.push({
                    caminho: img.dataset.path,
                    legenda: legendaInput ? legendaInput.value : ''
                });
            }
        });

        // Coleta de Assinaturas
        const canvasTecnico = document.getElementById('canvas-tecnico');
        const canvasCliente = document.getElementById('canvas-cliente');
        const nomeTecnico = document.getElementById('nome-tecnico').value;
        const nomeCliente = document.getElementById('nome-cliente').value;

        // Função auxiliar para verificar se canvas está vazio
        const isCanvasBlank = (canvas) => {
            const context = canvas.getContext('2d');
            const pixelBuffer = new Uint32Array(
                context.getImageData(0, 0, canvas.width, canvas.height).data.buffer
            );
            return !pixelBuffer.some(color => color !== 0);
        };

        const assinaturaTecnico = !isCanvasBlank(canvasTecnico) ? canvasTecnico.toDataURL('image/png') : '';
        const assinaturaCliente = !isCanvasBlank(canvasCliente) ? canvasCliente.toDataURL('image/png') : '';

        const payload = {
            cliente_id: clienteSelect.value,
            obra_nome: obraSelect.value,
            protocolo: protocolo,
            data_solicitacao: dataSolicitacao,
            solicitante: solicitante,
            tipo_atividade: atividadeSelect ? atividadeSelect.value : '',
            prioridade: prioridadeSelect ? prioridadeSelect.value : '',
            em_garantia: emGarantia,
            relato_cliente: relatoCliente,
            descricao_atividades: descricaoAtividades,
            conclusao: conclusao,
            deslocamento: document.getElementById('input-deslocamento') ? document.getElementById('input-deslocamento').value : '',
            servicos: horas,
            materiais: materiais,
            fotos: fotos,
            assinatura_tecnico: assinaturaTecnico,
            assinatura_cliente: assinaturaCliente,
            nome_tecnico_legivel: nomeTecnico,
            nome_cliente_legivel: nomeCliente
        };

        try {
            const response = await fetch('/rat/salvar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok) {
                customAlert('Sucesso', `RAT ${result.protocolo} salva com sucesso!`, 'success', () => {
                    window.location.href = '/rats';
                });
            } else {
                customAlert('Erro', `Erro ao salvar: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            customAlert('Erro', 'Erro ao conectar com o servidor.', 'error');
        } finally {
            // restore button
        }
    }


    // -------- Integração IA Socket.IO --------

    // Variável para guardar referência ao socket
    let socketQA = null;

    document.addEventListener("DOMContentLoaded", () => {
        // Aguarda um pequeno delay para garantir que o script do base.html (rodapé) rodou
        // Ou verifica diretamente se window.socket já existe.
        const initSocket = () => {
            if (window.socket) {
                socketQA = window.socket;
                console.log("✅ Socket IA vinculado com sucesso.");

                // Configura listeners
                socketQA.on('relatorio_gerado_sucesso', (data) => {
                    const btn = document.getElementById('btn-ia-gerar');
                    if (btn) {
                        btn.disabled = false;
                        btn.innerHTML = '<span class="material-symbols-outlined text-sm group-hover:animate-pulse">auto_awesome</span> Preencher com IA';
                    }

                    const txtDesc = document.getElementById('txt-descricao');
                    const txtConclusao = document.getElementById('txt-conclusao');

                    if (txtDesc && data.descricao) txtDesc.value = data.descricao;
                    if (txtConclusao && data.conclusao) txtConclusao.value = data.conclusao;
                });

                socketQA.on('erro_ia', (data) => {
                    const btn = document.getElementById('btn-ia-gerar');
                    if (btn) {
                        btn.disabled = false;
                        btn.innerHTML = '<span class="material-symbols-outlined text-sm">error</span> Erro';
                    }
                    customAlert('Erro IA', data.message, 'error');
                });

            } else {
                console.warn("Socket.IO ainda não disponível. Retentando em 500ms...");
                setTimeout(initSocket, 500);
            }
        };

        // Inicia verificação
        initSocket();
    });

    function gerarRelatorioIA() {
        if (!socketQA) {
            customAlert('Erro', "Conexão Socket.IO não inicializada. Tente recarregar a página.", 'error');
            return;
        }

        const btn = document.getElementById('btn-ia-gerar');
        const originalText = '<span class="material-symbols-outlined text-sm group-hover:animate-pulse">auto_awesome</span> Preencher com IA';

        const relato = document.getElementById('txt-relato').value;
        const atividadeSelect = document.getElementById('select-atividade');
        const deslocamento = document.getElementById('input-deslocamento') ? document.getElementById('input-deslocamento').value : '';

        if (!relato) {
            customAlert('Atenção', 'Por favor, preencha o Relato do Cliente antes de gerar com IA.', 'warning');
            return;
        }

        // Coleta de Horas
        const horas = [];
        document.querySelectorAll('#tbody-horas tr').forEach(row => {
            const inputs = row.querySelectorAll('input');
            const executanteSelect = row.querySelector('select');

            if (inputs.length >= 2 && inputs[0].value) {
                horas.push({
                    data: inputs[0].value,
                    inicio: inputs[1].value,
                    fim: inputs[2].value,
                    executante: executanteSelect ? executanteSelect.options[executanteSelect.selectedIndex].text : '',
                    observacao: ''
                });
            }
        });

        // Coleta de Materiais
        const materiais = [];
        document.querySelectorAll('#tbody-materiais tr').forEach(row => {
            const desc = row.querySelector('.input-descricao').value;
            const qtd = row.querySelector('.input-qtd').value;
            const un = row.querySelector('.input-unidade').value;

            if (desc) {
                materiais.push({
                    descricao: desc,
                    quantidade: qtd,
                    unidade: un
                });
            }
        });

        btn.disabled = true;
        btn.innerHTML = '<span class="material-symbols-outlined text-sm animate-spin">refresh</span> Gerando...';

        socketQA.emit('gerar_relatorio_ia', {
            relato_cliente: relato,
            tipo_atividade: atividadeSelect ? atividadeSelect.value : 'Atendimento',
            deslocamento: deslocamento,
            servicos: horas,
            materiais: materiais
        });

        // Timeout reset
        setTimeout(() => {
            if (btn.disabled) {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        }, 20000);
    }

    // Bind no botão de salvar
    document.querySelector('button.bg-primary.text-white.shadow-\\[0_0_15px_rgba\\(19\\,127\\,236\\,0\\.3\\)\\]').addEventListener('click', salvarRat);

</script>

{% if rat %}
<div class="max-w-5xl mx-auto pb-20">
    <!-- <header class="mb-8">
        <div class="flex items-center justify-between">
            <h1 class="text-3xl font-bold rat-text-primary tracking-tight">Editar RAT</h1>
            <div class="flex items-center gap-3">
                <a href="/rat/pdf/{{ rat.id }}?mode=preview" target="_blank"
                    class="px-3 py-1.5 bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-bold transition-colors flex items-center gap-1">
                    <span class="material-symbols-outlined text-[16px]">visibility</span> Prev
                </a>
                <a href="/rat/pdf/{{ rat.id }}?mode=download"
                    class="px-3 py-1.5 bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-bold transition-colors flex items-center gap-1">
                    <span class="material-symbols-outlined text-[16px]">download</span> PDF
                </a>
                <span class="px-3 py-1 bg-primary/20 text-primary rounded-lg text-sm font-bold">
                    {{ rat.protocolo }}
                </span>
            </div>
        </div>
        <p class="rat-text-muted mt-2">Atualize as informações técnicas do relatório.</p>
    </header> -->

    <div class="p-6 space-y-6">
        <!-- Info Básica (Read Only) -->
        <section class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
            <h3 class="rat-text-primary text-lg font-bold mb-4 flex items-center gap-2">
                <span class="material-symbols-outlined text-primary">info</span>
                Informações do Chamado
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                    <label class="block text-xs font-medium rat-text-muted mb-1">Cliente</label>
                    <div class="rat-input p-2 font-medium">
                        {{ rat.obra_nome }}
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-medium rat-text-muted mb-1">Solicitante</label>
                    <div class="rat-input p-2">
                        {{ rat.solicitante or '-' }}
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-medium rat-text-muted mb-1">Tipo de
                        Atividade</label>
                    <div class="rat-input p-2">
                        {{ rat.tipo_atividade or '-' }}
                    </div>
                </div>
            </div>
        </section>

        <form id="form-editar-rat" class="space-y-6">
            <input type="hidden" id="rat-id" value="{{ rat.id }}">
            <input type="hidden" id="rat-relato-cliente" value="{{ rat.relato_cliente }}">

            <!-- Horas de Serviço -->
            <section
                class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
                <div
                    class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-primary">schedule</span>
                        <h3 class="rat-text-primary text-lg font-bold">Horas de Serviço</h3>
                    </div>
                    <button type="button" id="btn-adicionar-hora"
                        class="text-xs font-bold text-primary hover:text-white bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">
                        <span class="material-symbols-outlined text-sm">add</span> Adicionar
                    </button>
                </div>
                <div class="rat-bg-surface overflow-x-auto">
                    <table class="rat-bg-surface w-full text-left border-collapse">
                        <thead class="rat-bg-surface">
                            <tr class="dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                    Data
                                </th>
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                    Início
                                </th>
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                    Fim
                                </th>
                                <th class="p-4 text-xs font-medium rat-text-muted uppercase tracking-wider">
                                    Executante
                                </th>
                                <th class="p-4 text-xs font-medium text-text-secondary uppercase tracking-wider w-10">
                                </th>
                            </tr>
                        </thead>
                        <tbody id="tbody-horas" class="divide-y divide-slate-200 dark:divide-slate-800">
                            {% for svc in servicos %}
                            <tr class="group hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors">
                                <td class="p-3"><input type="date" class="rat-input text-sm w-full h-9 px-3"
                                        value="{{ svc.data_servico }}" />
                                </td>
                                <td class="p-3"><input type="time" class="rat-input text-sm w-full h-9 px-3"
                                        value="{{ svc.hora_inicio }}" onchange="calcularTotalHoras()" />
                                </td>
                                <td class="p-3"><input type="time" class="rat-input text-sm w-full h-9 px-3"
                                        value="{{ svc.hora_fim }}" onchange="calcularTotalHoras()" />
                                </td>
                                <td class="p-3">
                                    <select class="rat-input rat-select text-sm w-full h-9 px-3">
                                        <option value="" disabled selected>Selecione...</option>
                                        {% for user in usuarios %}
                                        <option value="{{ user.id }}" {% if user.id==svc.executante_id %}selected{%
                                            endif %}>
                                            {{ user.nome }}
                                        </option>
                                        {% endfor %}
                                    </select>
                                </td>
                                <td class="p-3 text-center">
                                    <button type="button" class="rat-text-muted hover:text-red-500 transition-colors"
                                        onclick="removerLinha(this)">
                                        <span class="material-symbols-outlined text-lg">delete</span>
                                    </button>
                                </td>
                            </tr>
                            {% else %}
                            <!-- Empty Row Template if no services -->
                            <tr class="group hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors">
                                <td class="p-3"><input type="date" class="rat-input text-sm w-full h-9 px-3" />
                                </td>
                                <td class="p-3"><input type="time" class="rat-input text-sm w-full h-9 px-3"
                                        onchange="calcularTotalHoras()" /></td>
                                <td class="p-3"><input type="time" class="rat-input text-sm w-full h-9 px-3"
                                        onchange="calcularTotalHoras()" /></td>
                                <td class="p-3">
                                    <select class="rat-input rat-select text-sm w-full h-9 px-3">
                                        <option value="" disabled selected>Selecione...</option>
                                        {% for user in usuarios %}
                                        <option value="{{ user.id }}">{{ user.nome }}</option>
                                        {% endfor %}
                                    </select>
                                </td>
                                <td class="p-3 text-center">
                                    <button type="button" class="rat-text-muted hover:text-red-500 transition-colors"
                                        onclick="removerLinha(this)">
                                        <span class="material-symbols-outlined text-lg">delete</span>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                        <tfoot>
                            <tr class="dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800">
                                <td colspan="2" class="p-4 text-left">
                                    <div class="flex items-center gap-2">
                                        <span class="text-sm font-medium rat-text-muted">Deslocamento:</span>
                                        <input id="input-deslocamento" type="text"
                                            class="rat-input text-sm h-9 px-3 w-48" placeholder="Ex: 150km ou Remoto"
                                            value="{{ rat.deslocamento or '' }}">
                                    </div>
                                </td>
                                <td class="p-4 text-right text-sm font-bold rat-text-primary">Total de Horas:</td>
                                <td class="p-4 text-left text-sm font-bold text-primary" id="total-horas-display">0.00
                                </td>
                                <td></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </section>

            <!-- Materiais Utilizados -->
            <section
                class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-visible shadow-sm">
                <div
                    class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-primary">inventory_2</span>
                        <h3 class="rat-text-primary text-lg font-bold">Materiais Utilizados</h3>
                    </div>
                    <button type="button" id="btn-adicionar-material"
                        class="text-xs font-bold text-primary hover:text-white bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">
                        <span class="material-symbols-outlined text-sm">add</span> Adicionar Material
                    </button>
                </div>
                <div class="overflow-visible">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                                <th class="p-4 text-xs font-medium text-text-secondary uppercase tracking-wider w-24">
                                    Cód.</th>
                                <th class="p-4 text-xs font-medium text-text-secondary uppercase tracking-wider">
                                    Descrição</th>
                                <th class="p-4 text-xs font-medium text-text-secondary uppercase tracking-wider">
                                    Fabricante</th>
                                <th class="p-4 text-xs font-medium text-text-secondary uppercase tracking-wider w-20">
                                    Qtd</th>
                                <th class="p-4 text-xs font-medium text-text-secondary uppercase tracking-wider w-24">
                                    Unidade</th>
                                <th class="p-4 text-xs font-medium text-text-secondary uppercase tracking-wider w-10">
                                </th>
                            </tr>
                        </thead>
                        <tbody id="tbody-materiais" class="divide-y divide-slate-200 dark:divide-slate-800">
                            {% for mat in materiais %}
                            <tr class="group hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors relative">
                                <td class="p-3"><input class="rat-input text-sm w-full h-9 px-3 input-codigo"
                                        placeholder="SKU" type="text" value="{{ mat.codigo_engesep or '' }}" readonly />
                                </td>
                                <td class="p-3 relative">
                                    <input class="rat-input text-sm w-full h-9 px-3 input-descricao"
                                        placeholder="Buscar produto..." type="text" autocomplete="off"
                                        oninput="buscarProduto(this)" value="{{ mat.descricao or '' }}" />
                                    <div
                                        class="absolute top-11 left-0 right-0 rat-bg-surface border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 hidden results-container max-h-60 overflow-y-auto">
                                    </div>
                                </td>
                                <td class="p-3"><input class="rat-input text-sm w-full h-9 px-3 input-fabricante"
                                        placeholder="Marca" type="text" value="{{ mat.fabricante or '' }}" readonly />
                                </td>
                                <td class="p-3"><input class="rat-input text-sm w-full h-9 px-3 text-center input-qtd"
                                        type="number" value="{{ mat.quantidade or 1 }}" step="0.01" /></td>
                                <td class="p-3">
                                    <input class="rat-input text-sm w-full h-9 px-2 input-unidade" type="text"
                                        value="{{ mat.unidade or 'UN' }}" readonly />
                                </td>
                                <td class="p-3 text-center">
                                    <button type="button" class="rat-text-muted hover:text-red-500 transition-colors"
                                        onclick="removerLinhaMaterial(this)">
                                        <span class="material-symbols-outlined text-lg">delete</span>
                                    </button>
                                </td>
                            </tr>
                            {% else %}
                            <tr class="group hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors relative">
                                <td class="p-3"><input class="rat-input text-sm w-full h-9 px-3 input-codigo"
                                        placeholder="SKU" type="text" readonly /></td>
                                <td class="p-3 relative">
                                    <input class="rat-input text-sm w-full h-9 px-3 input-descricao"
                                        placeholder="Buscar produto..." type="text" autocomplete="off"
                                        oninput="buscarProduto(this)" />
                                    <div
                                        class="absolute top-11 left-0 right-0 rat-bg-surface border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 hidden results-container max-h-60 overflow-y-auto">
                                    </div>
                                </td>
                                <td class="p-3"><input class="rat-input text-sm w-full h-9 px-3 input-fabricante"
                                        placeholder="Marca" type="text" readonly /></td>
                                <td class="p-3"><input class="rat-input text-sm w-full h-9 px-3 text-center input-qtd"
                                        type="number" value="1" step="0.01" /></td>
                                <td class="p-3">
                                    <input class="rat-input text-sm w-full h-9 px-2 input-unidade" type="text"
                                        readonly />
                                </td>
                                <td class="p-3 text-center">
                                    <button type="button" class="rat-text-muted hover:text-red-500 transition-colors"
                                        onclick="removerLinhaMaterial(this)">
                                        <span class="material-symbols-outlined text-lg">delete</span>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Relatório Técnico -->
            <section
                class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
                <div
                    class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-primary">article</span>
                        <h3 class="rat-text-primary text-lg font-bold">Relatório Técnico</h3>
                    </div>
                    <button type="button" onclick="gerarRelatorioIA()" id="btn-ia-gerar"
                        class="text-xs font-bold text-white bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 px-3 py-1.5 rounded-lg transition-all shadow-md flex items-center gap-1 group">
                        <span class="material-symbols-outlined text-sm group-hover:animate-pulse">auto_awesome</span>
                        Preencher com IA
                    </button>
                </div>
                <div class="p-6 grid grid-cols-1 gap-6">
                    <label class="flex flex-col gap-2">
                        <span class="text-sm font-medium rat-text-muted">Descrição das Atividades
                            Realizadas</span>
                        <textarea id="txt-descricao"
                            class="w-full rat-input rounded-xl p-4 resize-none placeholder-slate-400"
                            placeholder="Detalhamento técnico..."
                            rows="6">{{ rat.descricao_atividades or '' }}</textarea>
                    </label>
                    <label class="flex flex-col gap-2">
                        <span class="text-sm font-medium rat-text-muted">Conclusão e Pendências</span>
                        <textarea id="txt-conclusao"
                            class="w-full rat-input rounded-xl p-4 resize-none placeholder-slate-400"
                            rows="4">{{ rat.conclusao or '' }}</textarea>
                    </label>
                </div>
            </section>

            <!-- Fotos e Assinaturas -->
            <!-- Nota: Assinaturas não serão editáveis aqui por simplicidade e integridade, salvo se necessário -->
            <section
                class="rounded-xl rat-bg-surface border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
                <div
                    class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-primary">photo_camera</span>
                        <h3 class="rat-text-primary text-lg font-bold">Fotos & Assinaturas</h3>
                    </div>
                </div>
                <div class="p-6">
                    <!-- Upload Area -->
                    <div id="dropzone"
                        class="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl rat-bg-main p-8 text-center hover:border-primary transition-colors cursor-pointer group mb-6 relative">
                        <input type="file" multiple accept="image/*" class="absolute inset-0 opacity-0 cursor-pointer"
                            id="file-input" onchange="handleFileSelect(event)">
                        <div class="pointer-events-none">
                            <span
                                class="material-symbols-outlined text-4xl rat-text-muted group-hover:text-primary transition-colors mb-2">cloud_upload</span>
                            <p class="text-sm rat-text-muted group-hover:rat-text-primary transition-colors">
                                Arraste fotos aqui ou <span class="text-primary font-bold">clique para selecionar</span>
                            </p>
                            <p class="text-xs rat-text-muted mt-1">PNG, JPG até 5MB</p>
                        </div>
                    </div>

                    <!-- Gallery Grid -->
                    <div id="gallery" class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {% for foto in fotos %}
                        <div
                            class="relative group aspect-square rat-bg-main rounded-lg overflow-hidden border border-slate-200 dark:border-slate-800">
                            <img src="{{ foto.caminho_arquivo }}" class="w-full h-full object-cover">
                            <div class="absolute inset-x-0 bottom-0 bg-black/60 p-2 backdrop-blur-sm">
                                <input type="text" value="{{ foto.legenda or '' }}"
                                    class="w-full bg-transparent border-none text-xs text-white p-0 placeholder:text-gray-400 focus:ring-0 existing-caption"
                                    placeholder="Legenda...">
                            </div>
                            <button type="button" onclick="marcarComoDeletada(this, {{ foto.id }})"
                                class="absolute top-2 right-2 p-1 bg-red-500/80 text-white rounded opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600">
                                <span class="material-symbols-outlined text-sm">delete</span>
                            </button>
                        </div>
                        {% endfor %}
                    </div>
                    <!-- Hidden input to store deleted photo IDs -->
                    <input type="hidden" id="deleted-photos" value="">
                </div>
            </section>

            <!-- Actions -->
            <div class="flex items-center justify-end gap-4">
                <a href="/"
                    class="px-6 py-3 rounded-xl border border-slate-300 dark:border-slate-700 rat-text-muted font-medium hover:rat-text-primary hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                    Cancelar
                </a>
                <button type="button" onclick="salvarAlteracoes()"
                    class="px-8 py-3 rounded-xl bg-primary hover:bg-blue-600 text-white font-bold shadow-lg shadow-primary/20 transition-all transform hover:scale-105">
                    Salvar Alterações
                </button>
            </div>

        </form>
    </div>
</div>

<script>
    // Inicializar total de horas
    document.addEventListener('DOMContentLoaded', () => {
        calcularTotalHoras();
    });

    // -------- Gerenciamento de Horas --------
    document.getElementById('btn-adicionar-hora').addEventListener('click', function () {
        const tbody = document.getElementById('tbody-horas');
        const novaLinha = tbody.rows[0].cloneNode(true);
        // Limpar inputs e selects
        novaLinha.querySelectorAll('input').forEach(input => input.value = '');
        novaLinha.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
        tbody.appendChild(novaLinha);
    });

    function removerLinha(btn) {
        const row = btn.closest('tr');
        const tbody = document.getElementById('tbody-horas');
        if (tbody.rows.length > 1) {
            row.remove();
        } else {
            row.querySelectorAll('input').forEach(input => input.value = '');
        }
        calcularTotalHoras();
    }

    function calcularTotalHoras() {
        let totalMinutos = 0;
        document.querySelectorAll('#tbody-horas tr').forEach(row => {
            const hInicio = row.cells[1].querySelector('input').value;
            const hFim = row.cells[2].querySelector('input').value; // Correção índice (Date is 0, Start 1, End 2)

            if (hInicio && hFim) {
                const [h1, m1] = hInicio.split(':').map(Number);
                const [h2, m2] = hFim.split(':').map(Number);

                let minInicio = h1 * 60 + m1;
                let minFim = h2 * 60 + m2;

                let diff = minFim - minInicio;
                if (diff < 0) diff += 24 * 60; // Passou da meia noite

                totalMinutos += diff;
            }
        });
        const horas = Math.floor(totalMinutos / 60);
        const minutos = totalMinutos % 60;
        document.getElementById('total-horas-display').textContent =
            `${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}h`;
    }

    // -------- Gerenciamento de Materiais --------
    // (Mesma lógica do _criarrat.html + Autocomplete)

    document.getElementById('btn-adicionar-material').addEventListener('click', function () {
        const tbody = document.getElementById('tbody-materiais');
        const novaLinha = tbody.rows[0].cloneNode(true);

        // Limpar values
        novaLinha.querySelectorAll('input').forEach(i => {
            if (i.type === 'number') i.value = 1;
            else i.value = '';
        });

        // Reset results container
        const resultsContainer = novaLinha.querySelector('.results-container');
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
            resultsContainer.classList.add('hidden');
        }

        tbody.appendChild(novaLinha);
    });

    function removerLinhaMaterial(btn) {
        const row = btn.closest('tr');
        const tbody = document.getElementById('tbody-materiais');
        if (tbody.rows.length > 1) row.remove();
        else {
            row.querySelectorAll('input').forEach(i => {
                if (i.type === 'number') i.value = 1;
                else i.value = '';
            });
        }
    }

    // Logica Autocomplete (Duplicated from _criarrat.html for simple autonomy)
    let searchTimeout = null;

    async function buscarProduto(input) {
        const tr = input.closest('tr');
        const resultsDiv = tr.querySelector('.results-container');
        const query = input.value;

        if (query.length < 2) {
            resultsDiv.classList.add('hidden');
            return;
        }

        if (searchTimeout) clearTimeout(searchTimeout);

        searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/produtos/buscar?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                resultsDiv.innerHTML = '';
                if (data.results && data.results.length > 0) {
                    data.results.forEach(prod => {
                        const div = document.createElement('div');
                        div.className = "px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer text-sm rat-text-primary";
                        div.innerHTML = `
                            <div class="font-bold rat-text-primary">${prod.codigo_produto}</div>
                            <div class="text-xs rat-text-muted">${prod.descricao}</div>
                        `;
                        div.onclick = () => selecionarProduto(tr, prod);
                        resultsDiv.appendChild(div);
                    });
                    resultsDiv.classList.remove('hidden');
                } else {
                    resultsDiv.innerHTML = '<div class="px-3 py-2 text-xs text-gray-500">Nenhum produto encontrado.</div>';
                    resultsDiv.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Erro:', error);
            }
        }, 300);
    }

    function selecionarProduto(tr, produto) {
        tr.querySelector('.input-codigo').value = produto.codigo_produto || '';
        tr.querySelector('.input-descricao').value = produto.descricao || '';
        tr.querySelector('.input-fabricante').value = produto.marca || '';
        tr.querySelector('.input-unidade').value = produto.unidade || 'UN';
        tr.querySelector('.results-container').classList.add('hidden');
    }

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.results-container') && !e.target.closest('.input-descricao')) {
            document.querySelectorAll('.results-container').forEach(el => el.classList.add('hidden'));
        }
    });

    // -------- Gerenciamento de Fotos (Upload + Delete) --------
    const uploadedFiles = []; // Guarda novos arquivos
    const deletedPhotoIds = []; // Guarda IDs de fotos existentes removidas

    function handleFileSelect(evt) {
        const files = Array.from(evt.target.files);
        if (!files.length) return;

        const gallery = document.getElementById('gallery');

        files.forEach(file => {
            uploadedFiles.push(file); // Store file object

            const reader = new FileReader();
            reader.onload = function (e) {
                const div = document.createElement('div');
                div.className = "relative group aspect-square rat-bg-main rounded-lg overflow-hidden border border-slate-200 dark:border-slate-800";
                div.innerHTML = `
                    <img src="${e.target.result}" class="w-full h-full object-cover">
                    <div class="absolute inset-x-0 bottom-0 bg-black/60 p-2 backdrop-blur-sm">
                        <input type="text" class="w-full bg-transparent border-none text-xs text-white p-0 placeholder:text-gray-400 focus:ring-0 new-caption"
                            placeholder="Legenda...">
                    </div>
                    <button type="button" onclick="removerNovaFoto(this, '${file.name}')" 
                        class="absolute top-2 right-2 p-1 bg-red-500/80 text-white rounded opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600">
                        <span class="material-symbols-outlined text-sm">delete</span>
                    </button>
                `;
                gallery.appendChild(div);
            }
            reader.readAsDataURL(file);
        });
    }

    function removerNovaFoto(btn, fileName) {
        const idx = uploadedFiles.findIndex(f => f.name === fileName);
        if (idx > -1) uploadedFiles.splice(idx, 1);
        btn.closest('div').remove();
    }

    function marcarComoDeletada(btn, id) {
        deletedPhotoIds.push(id);
        btn.closest('div').classList.add('opacity-50', 'pointer-events-none');
        btn.closest('div').style.border = '2px solid red';
    }

    // -------- Salvar Alterações --------
    async function salvarAlteracoes() {
        const ratId = document.getElementById('rat-id').value;
        const descricao = document.getElementById('txt-descricao').value;
        const conclusao = document.getElementById('txt-conclusao').value;

        // Coleta de Horas
        const horas = [];
        document.querySelectorAll('#tbody-horas tr').forEach(row => {
            const data = row.cells[0].querySelector('input').value;
            const inicio = row.cells[1].querySelector('input').value;
            const fim = row.cells[2].querySelector('input').value;
            const executanteSelect = row.cells[3].querySelector('select');
            const executante = executanteSelect ? executanteSelect.value : '';

            if (data && inicio && fim) {
                horas.push({ data, inicio, fim, executante });
            }
        });

        // Coleta de Materiais
        const materiais = [];
        document.querySelectorAll('#tbody-materiais tr').forEach(row => {
            const codigo = row.querySelector('.input-codigo').value;
            const desc = row.querySelector('.input-descricao').value;
            const fab = row.querySelector('.input-fabricante').value;
            const qtd = row.querySelector('.input-qtd').value;
            const un = row.querySelector('.input-unidade').value;

            if (desc) {
                materiais.push({ codigo, descricao: desc, fabricante: fab, quantidade: qtd, unidade: un });
            }
        });

        // Coleta legendas das fotos existentes que NÃO foram deletadas
        const existingPhotosData = [];
        document.querySelectorAll('#gallery .relative').forEach(div => {
            // Se não for novo (sem img src data uri) e não deletado
            const img = div.querySelector('img');
            const captionInput = div.querySelector('.existing-caption');
            const deleteBtn = div.querySelector('button[onclick^="marcarComoDeletada"]');

            if (captionInput && deleteBtn) { // É uma foto existente
                // Extrair ID do onclick="marcarComoDeletada(this, 123)"
                const idMatch = deleteBtn.getAttribute('onclick').match(/(\d+)\)/);
                if (idMatch) {
                    const id = parseInt(idMatch[1]);
                    if (!deletedPhotoIds.includes(id)) {
                        existingPhotosData.push({ id: id, legenda: captionInput.value });
                    }
                }
            }
        });

        // Coleta legendas novas (ordem sincrônica com uploadedFiles)
        const newCaptions = [];
        document.querySelectorAll('#gallery .relative').forEach(div => {
            const cap = div.querySelector('.new-caption');
            if (cap) newCaptions.push(cap.value);
        });

        // Criação do Payload
        // Como temos arquivos, vamos usar FormData se fosse multipart, mas aqui o backend espera JSON e os arquivos separados? 
        // Não, salvar RAT original era JSON com base64? 
        // Vamos ver ControllerRat.py original: salvarrat usa request.json e base64 para assinaturas, mas upload_foto era separado?
        // Mas aqui queremos salvar tudo de uma vez.
        // Opção: Enviar JSON com os dados e depois fazer upload das fotos novas, ou enviar tudo JSON com base64 das fotos.

        // Vamos usar abordagem mista: enviar dados JSON primeiro, depois uploads se necessário, ou enviar JSON com base64.
        // Dado que fotos podem ser grandes, base64 aumenta 33%. Melhor FormData se possível, ou JSON.
        // Vamos usar Base64 para as novas fotos para simplificar compatibilidade com o que já foi feito (assinaturas).

        const newPhotosBase64 = await Promise.all(uploadedFiles.map(file => {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = () => resolve(reader.result);
                reader.onerror = error => reject(error);
            });
        }));

        const novasFotosPayload = newPhotosBase64.map((b64, idx) => ({
            conteudo: b64,
            legenda: newCaptions[idx] || ''
        }));

        const payload = {
            rat_id: ratId,
            descricao_atividades: descricao,
            conclusao: conclusao,
            deslocamento: document.getElementById('input-deslocamento').value,
            servicos: horas,
            materiais: materiais,
            fotos_existentes: existingPhotosData, // Para atualizar legendas
            ids_fotos_removidas: deletedPhotoIds,
            novas_fotos: novasFotosPayload
        };

        try {
            const response = await fetch('/rat/atualizar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                customAlert('Sucesso', 'RAT atualizado com sucesso!', 'success', () => {
                    window.location.href = '/rats';
                });
            } else {
                const err = await response.json();
                customAlert('Erro', 'Erro ao atualizar: ' + (err.message || 'Erro desconhecido'), 'error');
            }
        } catch (error) {
            console.error(error);
            customAlert('Erro', 'Erro de conexão ao salvar.', 'error');
        }
    }

    // -------- Integração IA Socket.IO --------

    // Variável para guardar referência ao socket
    let socketQA = null;

    document.addEventListener("DOMContentLoaded", () => {
        // Aguarda um pequeno delay para garantir que o script do base.html (rodapé) rodou
        // Ou verifica diretamente se window.socket já existe.
        const initSocket = () => {
            if (window.socket) {
                socketQA = window.socket;
                console.log("✅ Socket IA vinculado com sucesso (Edit mode).");

                // Configura listeners
                socketQA.on('relatorio_gerado_sucesso', (data) => {
                    const btn = document.getElementById('btn-ia-gerar');
                    if (btn) {
                        btn.disabled = false;
                        btn.innerHTML = '<span class="material-symbols-outlined text-sm group-hover:animate-pulse">auto_awesome</span> Preencher com IA';
                    }

                    const txtDesc = document.getElementById('txt-descricao');
                    const txtConclusao = document.getElementById('txt-conclusao');

                    if (txtDesc && data.descricao) txtDesc.value = data.descricao;
                    if (txtConclusao && data.conclusao) txtConclusao.value = data.conclusao;
                });

                socketQA.on('erro_ia', (data) => {
                    const btn = document.getElementById('btn-ia-gerar');
                    if (btn) {
                        btn.disabled = false;
                        btn.innerHTML = '<span class="material-symbols-outlined text-sm">error</span> Erro';
                    }
                    customAlert('Erro IA', data.message, 'error');
                });

            } else {
                console.warn("Socket.IO ainda não disponível. Retentando em 500ms...");
                setTimeout(initSocket, 500);
            }
        };

        // Inicia verificação
        initSocket();
    });

    function gerarRelatorioIA() {
        if (!socketQA) {
            customAlert('Erro', "Conexão Socket.IO não inicializada. Tente recarregar a página.", 'error');
            return;
        }

        const btn = document.getElementById('btn-ia-gerar');
        const originalText = '<span class="material-symbols-outlined text-sm group-hover:animate-pulse">auto_awesome</span> Preencher com IA';

        const relatoInput = document.getElementById('rat-relato-cliente');
        const relato = relatoInput ? relatoInput.value : '';
        const deslocamento = document.getElementById('input-deslocamento') ? document.getElementById('input-deslocamento').value : '';

        // Coleta de Horas
        const horas = [];
        document.querySelectorAll('#tbody-horas tr').forEach(row => {
            const data = row.querySelector('input[type="date"]')?.value;
            const inpsTime = row.querySelectorAll('input[type="time"]');

            if (data && inpsTime.length >= 2) {
                // Try to get executante
                const execSelect = row.cells[3].querySelector('select');
                // Se não for select, talvez seja texto? Em modificar é select.
                const executante = execSelect ? execSelect.options[execSelect.selectedIndex].text : '';

                horas.push({
                    data: data,
                    inicio: inpsTime[0].value,
                    fim: inpsTime[1].value,
                    executante: executante,
                    observacao: ''
                });
            }
        });

        // Coleta de Materiais
        const materiais = [];
        document.querySelectorAll('#tbody-materiais tr').forEach(row => {
            const desc = row.querySelector('.input-descricao').value;
            const qtd = row.querySelector('.input-qtd').value;
            const un = row.querySelector('.input-unidade').value;

            if (desc) {
                materiais.push({
                    descricao: desc,
                    quantidade: qtd,
                    unidade: un
                });
            }
        });

        btn.disabled = true;
        btn.innerHTML = '<span class="material-symbols-outlined text-sm animate-spin">refresh</span> Gerando...';

        socketQA.emit('gerar_relatorio_ia', {
            relato_cliente: relato,
            tipo_atividade: 'Manutenção',
            deslocamento: deslocamento,
            servicos: horas,
            materiais: materiais
        });

        setTimeout(() => {
            if (btn.disabled) {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        }, 20000);
    }
</script>
{% else %}
<div class="flex items-center justify-center p-20 text-[var(--color-text-muted)]">
    <p>Selecione um RAT para editar ou retorne à página inicial.</p>
</div>
{% endif %}

<div id="rat-table-container" class="rat-table-container lg:col-span-3">
    <div class="rat-table-header-panel">
        <h3 class="text-sm font-semibold text-[var(--color-text)]">Histórico Recente</h3>
        <div class="flex gap-2">
            <input type="text" placeholder="Buscar por cliente, técnico ou ID..." class="rat-search-input"
                id="search-rats-input" value="{{ search_query }}" onkeyup="debounceFilterRats()">
        </div>
    </div>
    <div class="rat-table-wrapper">
        <table class="rat-table">
            <thead>
                <tr>
                    <th>Protocolo</th>
                    <th>Data</th>
                    <th>Cliente / Obra</th>
                    <th>Técnico</th>
                    <th>Tipo</th>
                    <th>Solicitação</th>
                    <th>Financeiro</th>
                    <th class="text-right">Ações</th>
                </tr>
            </thead>
            <tbody>
                {% for rat in lista_rats %}
                <tr>
                    <td class="rat-table-primary-text">#{{ rat.protocolo }}</td>
                    <td>{{ rat.data_formatada }}</td>
                    <td>
                        <div class="rat-table-primary-text">{{ rat.obra_nome or 'N/A' }}</div>
                    </td>
                    <td>
                        <div class="flex items-center gap-2">
                            <div class="rat-user-avatar">
                                {{ rat.tecnico_nome[:2].upper() if rat.tecnico_nome else '??' }}
                            </div>
                            <span>{{ rat.tecnico_nome }}</span>
                        </div>
                    </td>
                    <td>
                        <span
                            class="rat-badge {{ 'rat-badge-blue' if rat.tipo_atividade == 'Manutenção Corretiva' else 'rat-badge-default' }}">
                            {{ rat.tipo_atividade or 'Geral' }}
                        </span>
                    </td>
                    <td class="rat-col-solicitacao">
                        <div class="rat-table-primary-text truncate" title="{{ rat.solicitante }}">
                            {{ rat.solicitante or 'N/I' }}
                        </div>
                        <div class="text-xs truncate" title="{{ rat.relato_cliente }}">
                            {{ rat.relato_cliente or '-' }}
                        </div>
                    </td>
                    <td>
                        {% set status = rat.status_financeiro or 'pendente_faturamento' %}
                        {% set status_colors = {
                        'nao_faturavel': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
                        'pendente_faturamento': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30
                        dark:text-yellow-300',
                        'aguardando_pagamento': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
                        'liquidado': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
                        'inadimplente': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                        } %}
                        <div class="relative w-full min-w-[140px] group">
                            <span
                                class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-current opacity-60 group-hover:opacity-100 transition-opacity">
                                <span class="material-icons text-[18px]">expand_more</span>
                            </span>
                            <select onchange="atualizarStatusFinanceiro(this, {{ rat.id }})"
                                class="appearance-none w-full text-xs font-bold rounded-lg pl-3 pr-8 py-2 border border-transparent hover:brightness-95 focus:brightness-100 focus:border-primary/30 focus:ring-2 focus:ring-primary/20 cursor-pointer outline-none transition-all shadow-sm {{ status_colors.get(status, 'bg-gray-100 text-gray-800') }}">
                                <option value="nao_faturavel"
                                    class="bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200" {% if
                                    status=='nao_faturavel' %}selected{% endif %}>Não Faturável</option>
                                <option value="pendente_faturamento"
                                    class="bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200" {% if
                                    status=='pendente_faturamento' %}selected{% endif %}>Pendente</option>
                                <option value="aguardando_pagamento"
                                    class="bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200" {% if
                                    status=='aguardando_pagamento' %}selected{% endif %}>Aguardando</option>
                                <option value="liquidado"
                                    class="bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200" {% if
                                    status=='liquidado' %}selected{% endif %}>Liquidado</option>
                                <option value="inadimplente"
                                    class="bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200" {% if
                                    status=='inadimplente' %}selected{% endif %}>Inadimplente</option>
                            </select>
                        </div>
                    </td>
                    <td class="text-right">
                        <div class="rat-actions">
                            <button onclick="verRat({{ rat.id }})" class="rat-action-btn text-blue-500"
                                title="Detalhes">
                                <span class="material-icons text-[18px]">visibility</span>
                            </button>
                            <a href="/rat/pdf/{{ rat.id }}?mode=preview" target="_blank"
                                class="rat-action-btn text-purple-500" title="PDF">
                                <span class="material-icons text-[18px]">picture_as_pdf</span>
                            </a>
                            <a href="/modificarrat/{{ rat.id }}" class="rat-action-btn text-emerald-500" title="Editar">
                                <span class="material-icons text-[18px]">edit</span>
                            </a>
                            <button onclick="confirmarExclusao({{ rat.id }})"
                                class="rat-action-btn text-red-500 hover:bg-red-500/10" title="Excluir">
                                <span class="material-icons text-[18px]">delete</span>
                            </button>
                        </div>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="8" class="text-center py-8 text-[var(--color-text-muted)]">Nenhum RAT encontrado.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <div class="rat-footer">
        <span class="text-xs text-[var(--color-text-muted)]">
            Página <span class="font-bold text-[var(--color-text)]">{{ current_page }}</span> de <span
                class="font-bold text-[var(--color-text)]">{{ total_pages }}</span>
        </span>
        <div class="flex gap-2">
            <button data-page="{{ current_page - 1 }}" onclick="changePage(event)" class="rat-pagination-btn"
                {{ 'disabled' if current_page <=1 }}>
                <span class="material-icons text-sm">chevron_left</span> Anterior
            </button>
            <button data-page="{{ current_page + 1 }}" onclick="changePage(event)" class="rat-pagination-btn"
                {{ 'disabled' if current_page>= total_pages }}>
                Próxima <span class="material-icons text-sm">chevron_right</span>
            </button>
        </div>
    </div>
</div>

<!-- Modal de Confirmação de Exclusão -->
<div id="modal-delete-auth" class="fixed inset-0 z-50 flex items-center justify-center hidden">
    <div class="fixed inset-0 bg-black/75 transition-opacity backdrop-blur-sm" onclick="fecharModalDelete()"></div>
    <div
        class="relative rat-bg-surface rounded-xl shadow-2xl p-6 w-full max-w-sm m-4 border border-slate-200 dark:border-slate-800">
        <h3 class="text-lg font-bold text-[var(--color-text)] mb-2">Confirmar Exclusão</h3>
        <p class="text-sm text-[var(--color-text-muted)] mb-4">
            Esta ação é irreversível. Digite a senha administrativa para confirmar.
        </p>
        <input type="password" id="delete-password"
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2 text-[var(--color-text)] focus:ring-2 focus:ring-red-500 mb-4"
            placeholder="Senha...">
        <div class="flex justify-end gap-3">
            <button onclick="fecharModalDelete()"
                class="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-lg text-sm font-medium hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
                Cancelar
            </button>
            <button onclick="executarExclusao()"
                class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center gap-2">
                Excluir
            </button>
        </div>
    </div>
</div>

<!-- Modal de Visualização RAT -->
<div id="modal-ver-rat" class="fixed inset-0 z-[60] flex items-center justify-center hidden"
    aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <!-- Backdrop with blur -->

    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" onclick="fecharModalRat()"></div>

    <!-- Modal Panel -->
    <div
        class="relative w-full max-w-5xl max-h-[90vh] flex flex-col rat-bg-surface rounded-2xl shadow-2xl transform transition-all m-4 overflow-hidden border border-slate-700/50">

        <!-- Header Sticky -->
        <div
            class="flex-none px-8 py-5 border-b border-slate-700/50 rat-bg-surface flex justify-between items-start z-10 shadow-sm">
            <div>
                <div class="flex items-center gap-3 mb-2">
                    <span
                        class="px-3 py-1 rounded-full bg-primary/20 text-blue-400 text-xs font-bold uppercase tracking-wider border border-primary/20">
                        RAT #<span id="modal-protocolo">--</span>
                    </span>
                    <span class="text-sm text-[var(--color-text-muted)] font-medium flex items-center gap-1">
                        <span class="material-icons text-[14px]">event</span>
                        <span id="modal-data">--/--/----</span>
                    </span>
                </div>
                <h2 class="text-2xl font-bold text-[var(--color-text)] leading-tight" id="modal-cliente">Cliente</h2>
                <div class="flex items-center gap-2 text-sm text-[var(--color-text-muted)] mt-1">
                    <span class="material-icons text-[16px]">location_on</span>
                    <span id="modal-obra">Obra</span>
                </div>
            </div>
            <button onclick="fecharModalRat()"
                class="text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors p-1 rounded-full hover:bg-white/5 outline-none">
                <span class="material-icons text-2xl">close</span>
            </button>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto custom-scrollbar rat-bg-main">
            <div class="p-8 space-y-8">
                <!-- Section: Info Geral -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Card: Solicitação -->
                    <div
                        class="md:col-span-1 rat-bg-surface p-5 rounded-xl border border-slate-700/50 shadow-sm h-full">
                        <h3
                            class="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wider mb-4 border-b border-slate-700/50 pb-2 flex items-center gap-2">
                            <span class="material-icons text-[16px]">info</span> Detalhes
                        </h3>
                        <div class="space-y-4">
                            <div>
                                <span class="text-xs text-[var(--color-text-muted)] block mb-1">Solicitante</span>
                                <span id="modal-solicitante"
                                    class="text-sm font-medium text-[var(--color-text)] block rat-bg-main px-3 py-2 rounded-lg border border-slate-700/30"></span>
                            </div>
                            <div>
                                <span class="text-xs text-[var(--color-text-muted)] block mb-1">Atividade</span>
                                <span id="modal-atividade"
                                    class="text-sm font-medium text-[var(--color-text)] block rat-bg-main px-3 py-2 rounded-lg border border-slate-700/30"></span>
                            </div>
                            <div>
                                <span class="text-xs text-[var(--color-text-muted)] block mb-1">Prioridade</span>
                                <span id="modal-prioridade"
                                    class="text-sm font-medium text-[var(--color-text)] block rat-bg-main px-3 py-2 rounded-lg border border-slate-700/30"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Card: Relato & Descrição -->
                    <div class="md:col-span-2 space-y-6">
                        <!-- Relato -->
                        <div class="rat-bg-surface p-5 rounded-xl border border-slate-700/50 shadow-sm">
                            <h3
                                class="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wider mb-3 flex items-center gap-2">
                                <span class="material-icons text-[16px]">record_voice_over</span> Relato do Cliente
                            </h3>
                            <p id="modal-relato"
                                class="text-sm text-[var(--color-text)] leading-relaxed rat-bg-main p-4 rounded-lg border border-slate-700/30">
                            </p>
                        </div>

                        <!-- Descrição -->
                        <div class="rat-bg-surface p-5 rounded-xl border border-slate-700/50 shadow-sm">
                            <h3
                                class="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wider mb-3 flex items-center gap-2">
                                <span class="material-icons text-[16px]">engineering</span> Descrição Técnica
                            </h3>
                            <p id="modal-descricao"
                                class="text-sm text-[var(--color-text)] leading-relaxed whitespace-pre-wrap rat-bg-main p-4 rounded-lg min-h-[80px] border border-slate-700/30">
                            </p>
                        </div>

                        <!-- Conclusão -->
                        <div class="rat-bg-surface p-5 rounded-xl border border-slate-700/50 shadow-sm">
                            <h3
                                class="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wider mb-3 flex items-center gap-2">
                                <span class="material-icons text-[16px]">check_circle</span> Conclusão
                            </h3>
                            <p id="modal-conclusao"
                                class="text-sm text-[var(--color-text)] leading-relaxed rat-bg-main p-4 rounded-lg border border-slate-700/30">
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Section: Serviços -->
                <div class="rat-bg-surface rounded-xl border border-slate-700/50 shadow-sm overflow-hidden">
                    <div
                        class="px-5 py-4 border-b border-slate-700/50 flex items-center justify-between rat-bg-surface">
                        <h3 class="text-sm font-bold text-[var(--color-text)] flex items-center gap-2">
                            <span class="material-icons text-primary text-[18px]">schedule</span> Horas de Serviço
                        </h3>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead
                                class="rat-bg-main text-xs uppercase text-[var(--color-text-muted)] font-semibold border-b border-slate-700/50">
                                <tr>
                                    <th class="px-5 py-3 w-32 font-medium">Data</th>
                                    <th class="px-5 py-3 w-24 font-medium">Início</th>
                                    <th class="px-5 py-3 w-24 font-medium">Fim</th>
                                    <th class="px-5 py-3 w-48 font-medium">Executante</th>
                                    <th class="px-5 py-3 font-medium">Observações</th>
                                </tr>
                            </thead>
                            <tbody id="modal-tbody-servicos"
                                class="divide-y divide-slate-700/30 text-[var(--color-text-muted)]"></tbody>
                        </table>
                    </div>
                </div>

                <!-- Section: Materiais -->
                <div class="rat-bg-surface rounded-xl border border-slate-700/50 shadow-sm overflow-hidden">
                    <div
                        class="px-5 py-4 border-b border-slate-700/50 flex items-center justify-between rat-bg-surface">
                        <h3 class="text-sm font-bold text-[var(--color-text)] flex items-center gap-2">
                            <span class="material-icons text-emerald-500 text-[18px]">inventory_2</span> Materiais
                        </h3>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead
                                class="rat-bg-main text-xs uppercase text-[var(--color-text-muted)] font-semibold border-b border-slate-700/50">
                                <tr>
                                    <th class="px-5 py-3 w-32 font-medium">Código</th>
                                    <th class="px-5 py-3 font-medium">Descrição</th>
                                    <th class="px-5 py-3 w-24 text-right font-medium">Qtd.</th>
                                    <th class="px-5 py-3 w-24 text-center font-medium">Un.</th>
                                </tr>
                            </thead>
                            <tbody id="modal-tbody-materiais"
                                class="divide-y divide-slate-700/30 text-[var(--color-text-muted)]"></tbody>
                        </table>
                    </div>
                </div>

                <!-- Section: Fotos & Assinaturas Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <!-- Fotos -->
                    <div>
                        <h3 class="text-sm font-bold text-[var(--color-text)] mb-4 flex items-center gap-2">
                            <span class="material-icons text-blue-400 text-[18px]">photo_library</span> Relatório
                            Fotográfico
                        </h3>
                        <div id="modal-grid-fotos" class="grid grid-cols-2 sm:grid-cols-3 gap-3"></div>
                        <p id="modal-no-fotos"
                            class="text-sm text-[var(--color-text-muted)] italic rat-bg-surface p-6 rounded-xl border border-slate-700/50 text-center border-dashed">
                            Nenhuma foto registrada.
                        </p>
                    </div>

                    <!-- Assinaturas -->
                    <div>
                        <h3 class="text-sm font-bold text-[var(--color-text)] mb-4 flex items-center gap-2">
                            <span class="material-icons text-purple-400 text-[18px]">draw</span> Assinaturas
                        </h3>
                        <div class="space-y-4">
                            <!-- Técnico -->
                            <div class="rat-bg-surface rounded-xl border border-slate-700/50 p-4">
                                <p
                                    class="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
                                    Técnico Responsável</p>
                                <div
                                    class="h-24 flex items-center justify-center rat-bg-main rounded-lg border border-dashed border-slate-700/50 overflow-hidden relative">
                                    <img id="modal-assinatura-tec" class="hf-full object-contain hidden max-h-full"
                                        src="" alt="Assinatura Técnico" />
                                    <span id="modal-no-sig-tec"
                                        class="text-xs text-[var(--color-text-muted)]">Pendente</span>
                                </div>
                            </div>
                            <!-- Cliente -->
                            <div class="rat-bg-surface rounded-xl border border-slate-700/50 p-4">
                                <p
                                    class="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
                                    Cliente / Responsável</p>
                                <div
                                    class="h-24 flex items-center justify-center rat-bg-main rounded-lg border border-dashed border-slate-700/50 overflow-hidden relative">
                                    <img id="modal-assinatura-cli" class="h-full object-contain hidden max-h-full"
                                        src="" alt="Assinatura Cliente" />
                                    <span id="modal-no-sig-cli"
                                        class="text-xs text-[var(--color-text-muted)]">Pendente</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <!-- Footer Actions -->
        <div class="flex-none px-8 py-5 border-t border-slate-700/50 rat-bg-surface flex justify-end gap-3 z-10">
            <button onclick="fecharModalRat()"
                class="px-5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm font-medium text-[var(--color-text)] hover:bg-white/10 transition-colors shadow-sm">
                Fechar
            </button>
            <a id="btn-print-pdf" href="#" target="_blank"
                class="px-5 py-2.5 bg-primary hover:bg-blue-600 text-white rounded-xl text-sm font-medium transition-colors shadow-lg shadow-blue-500/20 flex items-center gap-2">
                <span class="material-icons text-[18px]">print</span>
                Imprimir PDF
            </a>
        </div>
    </div>
</div>

<!-- Toast Container -->


<script>
    let ratIdToDelete = null;

    function confirmingDelete(id) {
        ratIdToDelete = id;
        document.getElementById('modal-delete-auth').classList.remove('hidden');
        document.getElementById('delete-password').value = '';
        document.getElementById('delete-password').focus();
    }

    function confirmarExclusao(id) {
        confirmingDelete(id);
    }

    function fecharModalDelete() {
        document.getElementById('modal-delete-auth').classList.add('hidden');
        ratIdToDelete = null;
    }

    async function executarExclusao() {
        if (!ratIdToDelete) return;

        const password = document.getElementById('delete-password').value;
        if (!password) {
            customAlert('Aviso', 'Por favor, digite a senha.', 'warning');
            return;
        }

        try {
            const response = await fetch('/rat/deletar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rat_id: ratIdToDelete, password: password })
            });

            const data = await response.json();

            if (response.ok) {
                fecharModalDelete(); // Close password modal first
                customAlert('Sucesso', 'RAT excluído com sucesso.', 'success', () => {
                    window.location.reload();
                });
            } else {
                fecharModalDelete();
                customAlert('Erro', 'Erro: ' + (data.message || 'Falha na exclusão.'), 'error');
            }
        } catch (error) {
            console.error('Erro:', error);
            fecharModalDelete();
            customAlert('Erro', 'Erro ao processar exclusão.', 'error');
        }
    }

    async function verRat(id) {
        try {
            // Mostrar loading ou algo similar se quiser
            const response = await fetch(`/rat/ver/${id}`);
            const data = await response.json();

            if (response.ok) {
                preencherModal(data);
                document.getElementById('modal-ver-rat').classList.remove('hidden');
                document.body.style.overflow = 'hidden'; // Evitar scroll no fundo
            } else {
                customAlert('Erro', 'Erro ao carregar RAT: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            customAlert('Erro', 'Erro ao buscar detalhes do RAT.', 'error');
        }
    }

    function fecharModalRat() {
        document.getElementById('modal-ver-rat').classList.add('hidden');
        document.body.style.overflow = 'auto';
    }

    function preencherModal(data) {
        const rat = data.rat;
        const servicos = data.servicos;
        const materiais = data.materiais;

        // Cabeçalho
        document.getElementById('modal-protocolo').innerText = rat.protocolo;
        document.getElementById('modal-data').innerText = rat.data_formatada || rat.data_emissao;
        document.getElementById('modal-cliente').innerText = rat.obra_nome;
        document.getElementById('modal-obra').innerText = `Obra: ${rat.obra_nome}`;

        // Link PDF
        const btnPrint = document.getElementById('btn-print-pdf');
        if (btnPrint) btnsPrint = btnPrint.href = `/rat/pdf/${rat.id}?mode=preview`;

        // Info
        document.getElementById('modal-solicitante').innerText = rat.solicitante || '-';
        document.getElementById('modal-atividade').innerText = rat.tipo_atividade || '-';
        document.getElementById('modal-prioridade').innerText = rat.prioridade || '-';

        // Textos
        // Usar innerText para tratar quebras de linha corretamente em CSS whitespace-pre-wrap ou usar textContent
        document.getElementById('modal-relato').innerText = rat.relato_cliente || 'Nenhum relato informado.';
        document.getElementById('modal-descricao').innerText = rat.descricao_atividades || 'Nenhuma descrição técnica informada.';
        document.getElementById('modal-conclusao').innerText = rat.conclusao || 'Nenhuma conclusão informada.';

        // Serviços
        const tbodyServicos = document.getElementById('modal-tbody-servicos');
        tbodyServicos.innerHTML = '';
        if (servicos && servicos.length > 0) {
            servicos.forEach(svc => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors";
                tr.innerHTML = `
<td class="px-5 py-3 text-slate-600 dark:text-slate-300 font-medium">${svc.data_servico || '-'}</td>
<td class="px-5 py-3 text-slate-600 dark:text-slate-300 font-mono text-xs">${svc.hora_inicio || '--:--'}</td>
<td class="px-5 py-3 text-slate-600 dark:text-slate-300 font-mono text-xs">${svc.hora_fim || '--:--'}</td>
<td class="px-5 py-3 text-slate-600 dark:text-slate-300">${svc.executante_nome || svc.executante_id || '-'}</td>
<td class="px-5 py-3 text-slate-500 dark:text-slate-400 italic text-xs max-w-[300px] break-words">${svc.observacoes ||
                    '-'}</td>
`;
                tbodyServicos.appendChild(tr);
            });
        } else {
            tbodyServicos.innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-slate-400 text-sm italic">Nenhum serviço registrado.</td></tr>';
        }

        // Materiais
        const tbodyMateriais = document.getElementById('modal-tbody-materiais');
        tbodyMateriais.innerHTML = '';
        if (materiais && materiais.length > 0) {
            materiais.forEach(mat => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors";
                tr.innerHTML = `
<td class="px-5 py-3 text-slate-600 dark:text-slate-300 font-mono text-xs">${mat.codigo_engesep || '-'}</td>
<td class="px-5 py-3 text-slate-600 dark:text-slate-300 font-medium">${mat.descricao || '-'}</td>
<td class="px-5 py-3 text-slate-600 dark:text-slate-300 font-bold text-right">${mat.quantidade ?
                        parseFloat(mat.quantidade).toFixed(2) : '-'}</td>
<td class="px-5 py-3 text-slate-500 dark:text-slate-400 text-xs text-center">${mat.unidade || 'UN'}</td>
`;
                tbodyMateriais.appendChild(tr);
            });
        } else {
            tbodyMateriais.innerHTML = '<tr><td colspan="4" class="px-6 py-4 text-center text-slate-400 text-sm italic">Nenhum material utilizado.</td></tr>';
        }

        // Fotos
        const gridFotos = document.getElementById('modal-grid-fotos');
        const noFotosMsg = document.getElementById('modal-no-fotos');
        const fotos = data.fotos;

        gridFotos.innerHTML = '';
        if (fotos && fotos.length > 0) {
            noFotosMsg.classList.add('hidden');
            fotos.forEach(foto => {
                const div = document.createElement('div');
                div.className = "relative group aspect-square bg-slate-100 dark:bg-slate-800 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-800 cursor-zoom-in";
                div.innerHTML = `
<img src="${foto.caminho_arquivo}"
    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
    alt="${foto.legenda || 'Foto RAT'}">
${foto.legenda ? `<div
    class="absolute bottom-0 left-0 right-0 bg-black/60 p-1 text-[10px] text-white truncate text-center">${foto.legenda}
</div>` : ''}
`;
                // Simple open in new tab for zoom
                div.onclick = () => window.open(foto.caminho_arquivo, '_blank');
                gridFotos.appendChild(div);
            });
        } else {
            noFotosMsg.classList.remove('hidden');
        }

        // Assinaturas
        const sigTecImg = document.getElementById('modal-assinatura-tec');
        const sigTecNo = document.getElementById('modal-no-sig-tec');

        if (rat.caminho_assinatura_tec) {
            sigTecImg.src = rat.caminho_assinatura_tec;
            sigTecImg.classList.remove('hidden');
            sigTecNo.classList.add('hidden');
        } else {
            sigTecImg.classList.add('hidden');
            sigTecNo.classList.remove('hidden');
        }

        const sigCliImg = document.getElementById('modal-assinatura-cli');
        const sigCliNo = document.getElementById('modal-no-sig-cli');

        if (rat.caminho_assinatura_cli) {
            sigCliImg.src = rat.caminho_assinatura_cli;
            sigCliImg.classList.remove('hidden');
            sigCliNo.classList.add('hidden');
        } else {
            sigCliImg.classList.add('hidden');
            sigCliNo.classList.remove('hidden');
        }
    }

    const statusColors = {
        'nao_faturavel': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
        'pendente_faturamento': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
        'aguardando_pagamento': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
        'liquidado': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
        'inadimplente': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
    };

    async function atualizarStatusFinanceiro(selectElement, ratId) {
        const novoStatus = selectElement.value;
        const oldClass = selectElement.className;

        // Feedback visual imediato (loading?) ou apenas troca a cor
        // Vamos trocar a cor imediatamente para "feels snappy"
        // Remove old generic classes first if any? No, just reset to base + new color
        const baseClasses = "appearance-none w-full text-xs font-bold rounded-lg pl-3 pr-8 py-2 border border-transparent hover:brightness-95 focus:brightness-100 focus:border-primary/30 focus:ring-2 focus:ring-primary/20 cursor-pointer outline-none transition-all shadow-sm";
        selectElement.className = `${baseClasses} ${statusColors[novoStatus] || ''}`;

        try {
            const response = await fetch('/rat/atualizar_status_financeiro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rat_id: ratId, novo_status: novoStatus })
            });

            const data = await response.json();

            if (!response.ok) {
                // Revert on error
                customAlert('Erro', 'Erro ao atualizar status: ' + data.message, 'error');
                // Reload or revert UI? Reload is safer for sync
                // location.reload();
            } else {
                // Sucesso
                customAlert('Sucesso', 'Status atualizado com sucesso', 'success');
                console.log('Status atualizado com sucesso');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            customAlert('Erro', 'Erro de conexão ao atualizar status.', 'error');
            // Reverter?
        }
    }


    let searchTimeout = null;

    // Server-side debounced search
    function debounceFilterRats() {
        const input = document.getElementById('search-rats-input');
        const term = input.value;

        if (searchTimeout) clearTimeout(searchTimeout);

        searchTimeout = setTimeout(() => {
            fetchRats(1, term);
        }, 500); // Wait 500ms after user stops typing
    }

    function changePage(event) {
        const btn = event.currentTarget;
        if (btn.disabled) return;
        const page = btn.dataset.page;
        const input = document.getElementById('search-rats-input');
        const term = input ? input.value : '';
        fetchRats(page, term);
    }

    async function fetchRats(page, term) {
        try {
            // Add loading indicator opacity to table
            const tableContainer = document.querySelector('.rat-table-wrapper');
            if (tableContainer) tableContainer.style.opacity = '0.5';

            let url = `/rats?partial=true&page=${page}`;
            if (term) {
                url += `&q=${encodeURIComponent(term)}`;
            }

            const response = await fetch(url);
            if (response.ok) {
                const html = await response.text();

                // Let's replace the whole container.
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;

                const newTableWrapper = tempDiv.querySelector('.rat-table-wrapper');
                const newFooter = tempDiv.querySelector('.rat-footer');

                if (newTableWrapper) {
                    document.querySelector('.rat-table-wrapper').innerHTML = newTableWrapper.innerHTML;
                }
                if (newFooter) {
                    document.querySelector('.rat-footer').innerHTML = newFooter.innerHTML;
                }

                // Update URL history without reload
                let newUrl = window.location.pathname + `?page=${page}`;
                if (term) newUrl += `&q=${encodeURIComponent(term)}`;
                window.history.pushState({ path: newUrl }, '', newUrl);

            } else {
                console.error('Erro ao buscar dados');
            }
        } catch (error) {
            console.error(error);
        } finally {
            const tableContainer = document.querySelector('.rat-table-wrapper');
            if (tableContainer) tableContainer.style.opacity = '1';
        }
    }
</script>

<!DOCTYPE html>
<html lang="pt-br">

<head>
    <meta charset="UTF-8" />
    <title>RAT - {{ rat.protocolo }}</title>

    <style>
        @page {
            size: A4;
            margin: 12mm 12mm 14mm 12mm;

            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-family: Helvetica, Arial, sans-serif;
                font-size: 8pt;
                color: #94a3b8;
            }
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 9.5pt;
            color: #0f172a;
            line-height: 1.35;
            margin: 0;
            padding: 0;
        }

        :root {
            --primary: #004680;
            --gray-50: #f8fafc;
            --gray-200: #e2e8f0;
            --gray-500: #64748b;
            --text: #0f172a;
        }

        img {
            max-width: 100%;
            height: auto;
        }

        /* Helpers */
        .text-center {
            text-align: center;
        }

        .text-right {
            text-align: right;
        }

        .font-bold {
            font-weight: 700;
        }

        .avoid-break {
            page-break-inside: avoid;
        }

        /* Header (tabela = previsível no WeasyPrint) */
        .header {
            width: 100%;
            border-bottom: 1px solid var(--gray-200);
            padding-bottom: 8px;
            margin-bottom: 10px;
        }

        .header td {
            vertical-align: middle;
            border: none;
            padding: 0;
        }

        .logo-wrapper {
            background: var(--primary);
            padding: 8px 14px;
            border-radius: 7px;
            display: inline-block;
        }

        .logo {
            height: 36px;
            width: auto;
            display: block;
        }

        .header-title {
            font-size: 15pt;
            color: var(--primary);
            font-weight: 700;
            letter-spacing: .3px;
            margin: 0;
            text-transform: uppercase;
        }

        .protocol {
            font-size: 10pt;
            font-weight: 700;
            color: var(--text);
            margin-top: 2px;
        }

        .issued {
            font-size: 8pt;
            color: var(--gray-500);
            margin-top: 2px;
        }

        /* Seções */
        .section-header {
            background: var(--primary);
            color: white;
            text-align: center;
            font-weight: 700;
            padding: 6px 10px;
            text-transform: uppercase;
            font-size: 9.5pt;
            border-radius: 4px;
            margin: 10px 0 6px 0;
            letter-spacing: .35px;
        }

        /* Tabelas */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0 0 8px 0;
            border-radius: 6px;
        }

        th,
        td {
            border: 1px solid var(--gray-200);
            padding: 6px 8px;
            vertical-align: top;
            font-size: 8.5pt;
        }

        thead th {
            background: #6d6d6d;
            color: white;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 7.8pt;
            letter-spacing: .4px;
        }

        /* Header-table (cliente/obra/cnpj/cidade) */
        .label-cell {
            background: var(--primary);
            color: white;
            font-weight: 700;
            text-transform: uppercase;
            width: 13%;
            font-size: 7.6pt;
            letter-spacing: .3px;
            vertical-align: middle;
        }

        .value-cell {
            font-weight: 700;
            color: var(--text);
            vertical-align: middle;
        }

        /* Cards */
        .card {
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            padding: 8px;
            background: white;
        }

        .card-title {
            background: #6d6d6d;
            color: white;
            font-weight: 700;
            font-size: 7.8pt;
            text-transform: uppercase;
            padding: 4px 8px;
            border-radius: 4px;
            margin: -8px -8px 8px -8px;
            text-align: center;
            letter-spacing: .3px;
        }

        .field {
            border-bottom: 1px solid var(--gray-200);
            padding: 6px 0;
        }

        .field:last-child {
            border-bottom: none;
        }

        .mini-label {
            font-size: 7.5pt;
            color: var(--gray-500);
        }

        .mini-value {
            font-size: 8.8pt;
            font-weight: 700;
            color: var(--text);
        }

        /* Descritivo */
        .description-box {
            border: 1px solid var(--gray-200);
            background: var(--gray-50);
            border-radius: 6px;
            padding: 10px;
            margin: 8px 0;
            page-break-inside: avoid;
        }

        .description-box strong {
            display: block;
            margin-bottom: 4px;
            color: var(--primary);
        }

        /* Layout “Horas de Serviços”: 2 colunas via tabela sem borda */
        .no-border {
            border: none !important;
        }

        /* Fotos: 2 colunas via tabela (evita flex/grid bugado) */
        .photo-table td {
            border: none;
            padding: 6px;
            width: 50%;
            vertical-align: top;
        }

        .photo-item {
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            padding: 6px;
            page-break-inside: avoid;
        }

        .photo-img {
            width: 100%;
            height: 210px;
            /* controla o “card” */
            object-fit: cover;
            /* corta sem distorcer */
            display: block;
            border-radius: 4px;
        }

        .photo-caption {
            margin-top: 6px;
            font-size: 8pt;
            color: var(--gray-500);
        }

        /* Assinaturas */
        .signatures {
            margin-top: 14px;
            page-break-inside: avoid;
        }

        .sign-table td {
            width: 50%;
            border: none;
            padding: 10px 8px;
            vertical-align: bottom;
        }

        .signature-line {
            height: 60px;
            border-bottom: 1px solid var(--gray-500);
            margin-bottom: 6px;
            position: relative;
        }

        .signature-img {
            max-height: 55px;
            width: auto;
            position: absolute;
            bottom: 2px;
            left: 0;
        }

        .signature-name {
            font-weight: 700;
            font-size: 9pt;
        }

        .signature-role {
            font-size: 8pt;
            color: var(--gray-500);
        }
    </style>
</head>

<body>

    <!-- HEADER -->
    <table class="header">
        <tr>
            <td style="width:42%;">
                <span class="logo-wrapper">
                    <img src="{{ logo_path }}" alt="Engesep" class="logo" />
                </span>
            </td>
            <td class="text-right">
                <div class="header-title">RELATÓRIO DE ASSISTÊNCIA TÉCNICA</div>
                <div class="protocol">Protocolo: #{{ rat.protocolo }}</div>
                <div class="issued">Emitido em: {{ rat.data_emissao_formatada }}</div>
            </td>
        </tr>
    </table>

    <!-- DADOS CLIENTE / OBRA -->
    <table class="avoid-break">
        <tr>
            <td class="label-cell">CLIENTE</td>
            <td class="value-cell">{{ rat.cliente_nome or '-' }}</td>
            <td class="label-cell">CNPJ</td>
            <td class="value-cell">{{ rat.cliente_cnpj or '-' }}</td>
        </tr>
        <tr>
            <td class="label-cell">OBRA</td>
            <td class="value-cell">{{ rat.obra_nome or '-' }}</td>
            <td class="label-cell">CIDADE</td>
            <td class="value-cell">{{ rat.cliente_cidade or '-' }}</td>
        </tr>
    </table>

    <!-- RESUMO -->
    <div class="section-header">RESUMO - CHAMADO</div>

    <table class="avoid-break" style="border:none;">
        <tr>
            <td class="no-border" style="width:50%; padding:0 6px 0 0;">
                <div class="card">
                    <div class="card-title">DADOS GERAIS</div>

                    <div class="field">
                        <div class="mini-label">Data Solicitada: <span style="color:var(--primary);">{{
                                rat.data_solicitacao or '-' }}</span></div>
                    </div>

                    <div class="field">
                        <div class="mini-label">Tipo Atividade: <span class="mini-value">{{ rat.tipo_atividade or
                                '-' }}</span></div>
                    </div>

                    <div class="field">
                        <div class="mini-label">Prioridade: <span class="mini-value">{{ rat.prioridade or
                                'Média' }}</span></div>
                    </div>

                    <div class="field">
                        <div class="mini-label">Solicitante: <span class="mini-value">{{ rat.solicitante or
                                '-' }}</span></div>
                    </div>

                    <div class="field">
                        <div class="mini-label">Local: <span class="mini-value">{{ rat.obra_nome or '-'
                                }}</span></div>
                    </div>

                    <div class="field">
                        <div class="mini-label">Garantia: <span class="mini-value">{{ 'SIM' if
                                rat.em_garantia else 'NÃO' }}</span></div>
                    </div>
                </div>
            </td>

            <td class="no-border" style="width:50%; padding:0 0 0 6px;">
                <div class="card">
                    <div class="card-title">RELATO CLIENTE</div>
                    <div style="min-height:160px; font-size:8.8pt;">
                        {{ rat.relato_cliente or '-' }}
                    </div>
                </div>
            </td>
        </tr>
    </table>

    <!-- HORAS DE SERVIÇOS -->
    <div class="section-header">HORAS DE SERVIÇOS</div>

    <table style="border:none;" class="avoid-break">
        <tr>
            <td class="no-border" style="width:70%; padding:0 6px 0 0; border-radius: 6px;">

                <table>
                    <thead>
                        <tr>
                            <th style="width:5%;">D</th>
                            <th style="width:20%;">Data</th>
                            <th style="width:13%;">Início(hrs)</th>
                            <th style="width:13%;">Fim(hrs)</th>
                            <th style="width:13%;">Tempo</th>
                            <th style="width:32%;">Obs.</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for svc in servicos %}
                        <tr>
                            <td class="text-center">D{{ loop.index }}</td>
                            <td>{{ svc.data_servico_formatada }}</td>
                            <td>{{ svc.hora_inicio }}</td>
                            <td>{{ svc.hora_fim }}</td>
                            <td class="text-center">{{ svc.tempo_decorrido }}</td>
                            <td>{{ svc.observacoes or '' }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="6" class="text-center">Nenhum registro.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>

            </td>

            <td class="no-border" style="width:30%; padding:0 0 0 6px;">
                <table>
                    <thead>
                        <tr>
                            <th colspan="2" class="text-center">EXECUTANTE</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="mini-label" style="width:35%;">Nome</td>
                            <td class="mini-value">{{ rat.tecnico_nome or '-' }}</td>
                        </tr>
                        <tr>
                            <td class="mini-label">Cargo</td>
                            <td class="mini-value">Técnico</td>
                        </tr>
                        <tr>
                            <td class="mini-label">Deslocamento</td>
                            <td class="mini-value">{{ rat.deslocamento or '-' }}</td>
                        </tr>
                        <tr>
                            <td class="mini-label">Horas</td>
                            <td class="mini-value">{{ rat.total_horas or '0.0' }}h</td>
                        </tr>
                    </tbody>
                </table>

            </td>
        </tr>
    </table>

    <!-- MATERIAIS -->
    <div class="section-header">MATERIAIS UTILIZADOS</div>

    <table class="avoid-break">
        <thead>
            <tr>
                <th style="width:15%;">Código</th>
                <th style="width:45%;">Descrição</th>
                <th style="width:20%;">Fabricante</th>
                <th style="width:10%;" class="text-center">Qtd.</th>
                <th style="width:10%;" class="text-center">Un.</th>
            </tr>
        </thead>
        <tbody>
            {% for mat in materiais %}
            <tr>
                <td>{{ mat.codigo_engesep or '-' }}</td>
                <td>{{ mat.descricao }}</td>
                <td>{{ mat.fabricante or '-' }}</td>
                <td class="text-center">{{ mat.quantidade }}</td>
                <td class="text-center">{{ mat.unidade }}</td>
            </tr>
            {% else %}
            <tr>
                <td colspan="5" class="text-center">Nenhum material utilizado.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <!-- RELATÓRIO DESCRITIVO -->
    <div class="section-header">RELATÓRIO DESCRITIVO</div>

    <div class="description-box">
        <strong>Atividades Realizadas</strong>
        {{ rat.descricao_atividades or 'Não informado.' }}
    </div>

    <div class="description-box">
        <strong>Conclusão / Pendências</strong>
        {{ rat.conclusao or 'Não informado.' }}
    </div>

    <!-- FOTOS -->
    {% if fotos %}
    <div style="page-break-before: always;"></div>
    <div class="section-header">RELATÓRIO FOTOGRÁFICO</div>

    <table class="photo-table">
        {% for foto in fotos %}
        {% if loop.index0 % 2 == 0 %}<tr>{% endif %}
            <td>
                <div class="photo-item">
                    <img src="{{ foto.caminho_absoluto }}" class="photo-img" alt="Foto {{ loop.index }}">
                    <div class="photo-caption">{{ foto.legenda or ('Foto ' ~ loop.index) }}</div>
                </div>
            </td>
            {% if loop.index0 % 2 == 1 %}
        </tr>{% endif %}
        {% endfor %}
        {% if fotos|length % 2 == 1 %}
        <td></td>
        </tr>
        {% endif %}
    </table>
    {% endif %}

    <!-- ASSINATURAS -->
    <div class="signatures">
        <div class="section-header">ASSINATURAS</div>

        <table class="sign-table">
            <tr>
                <td>
                    <div class="signature-line">
                        {% if rat.caminho_assinatura_tec_absoluto %}
                        <img src="{{ rat.caminho_assinatura_tec_absoluto }}" class="signature-img"
                            alt="Assinatura Técnico">
                        {% endif %}
                    </div>
                    <div class="signature-name">{{ rat.tecnico_nome or 'Técnico Responsável' }}</div>
                    <div class="signature-role">Técnico Engesep</div>
                </td>

                <td>
                    <div class="signature-line">
                        {% if rat.caminho_assinatura_cli_absoluto %}
                        <img src="{{ rat.caminho_assinatura_cli_absoluto }}" class="signature-img"
                            alt="Assinatura Cliente">
                        {% endif %}
                    </div>
                    <div class="signature-name">{{ rat.solicitante or 'Responsável Cliente' }}</div>
                    <div class="signature-role">Representante do Cliente</div>
                </td>
            </tr>
        </table>
    </div>

</body>

</html>