# libs/controllers/eventosController.py
from flask import render_template, request, jsonify
from libs.models.read import Read
from libs.models.create import Create
from libs.models.mock_data import DEVELOPER_MODE, get_mock_data
from libs.models.utils.utils import desempenho
import json
from datetime import datetime

class EventosController:
    def __init__(self):
        self.usinas = Read("op_usina")
        self.usuarios = Read("op_usuario")
        self.ocorrencias_create = Create("op_ocorrencia")
        
    @desempenho
    def registro_page(self):
        """Renderiza a página de registro de eventos"""
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            usinas = get_mock_data('op_usina')
            usuarios = get_mock_data('op_usuario')
        else:
            # Usa dados reais do banco de dados
            usinas = self.usinas.get_all()
            usuarios = self.usuarios.get_all()
        
        # Templates de texto pré-definidos
        templates = [
            {
                "id": "manutencao_preventiva",
                "nome": "Manutenção Preventiva",
                "texto": "Realizada manutenção preventiva conforme plano estabelecido. Todos os procedimentos foram executados de acordo com as normas de segurança."
            },
            {
                "id": "parada_emergencia",
                "nome": "Parada de Emergência",
                "texto": "Acionada parada de emergência devido a detecção de anomalia. Sistema desligado conforme protocolo de segurança."
            },
            {
                "id": "trip_geracao",
                "nome": "Trip de Geração",
                "texto": "Unidade geradora desligada automaticamente. Aguardando análise técnica para identificação da causa e liberação para retomada."
            },
            {
                "id": "falha_equipamento",
                "nome": "Falha de Equipamento",
                "texto": "Identificada falha no equipamento. Equipe técnica acionada para avaliação e correção."
            },
            {
                "id": "oscilacao_tensao",
                "nome": "Oscilação de Tensão",
                "texto": "Registrada oscilação de tensão fora dos parâmetros normais. Monitoramento contínuo ativado."
            }
        ]
        
        # Categorias disponíveis
        categorias = [
            "Operação/Humano",
            "Elétrica",
            "Hidráulica",
            "Mecânica",
            "Automação",
            "Segurança",
            "Ambiental"
        ]
        
        # Tipos de eventos
        tipos = [
            "Evento",
            "Alarme",
            "Trip",
            "Comando",
            "Manutenção"
        ]
        
        return render_template(
            "registro_eventos.html",
            usinas=usinas,
            usuarios=usuarios,
            templates=templates,
            categorias=categorias,
            tipos=tipos
        )
    
    @desempenho
    def criar_ocorrencia(self):
        """Cria uma nova ocorrência via POST"""
        try:
            data = request.get_json()
            
            # Validações básicas
            required_fields = ["usina_id", "tipo", "categoria", "unidade", "descricao"]
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"success": False, "error": f"Campo obrigatório: {field}"}), 400
            
            # Constrói metadata JSON
            requer_acao = data.get("requer_acao", False)
            metadata = {
                "requer_acao": requer_acao,
                "notificado_em": None,
                "responsavel_id": None,
                "assumido_em": None,
                "observacoes": None
            }
            
            # Prepara dados para inserção
            ocorrencia_data = {
                "usina_id": data["usina_id"],
                "operador_id": data.get("operador_id", 1),  # Default se não informado
                "tipo": data["tipo"],
                "categoria": data["categoria"],
                "unidade": data["unidade"],
                "tags": data.get("tags", ""),
                "playbook": data.get("playbook", ""),
                "template_texto": data.get("template_texto", ""),
                "descricao": data["descricao"],
                "status": "aberta",
                "severidade": data.get("severidade", "média"),
                "origem": "humano",
                "metadata": json.dumps(metadata)
            }
            
            # Insere no banco
            result = self.ocorrencias_create.insert(ocorrencia_data)
            
            if result:
                return jsonify({
                    "success": True,
                    "message": "Ocorrência registrada com sucesso!",
                    "id": result
                }), 201
            else:
                return jsonify({
                    "success": False,
                    "error": "Erro ao registrar ocorrência"
                }), 500
                
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
