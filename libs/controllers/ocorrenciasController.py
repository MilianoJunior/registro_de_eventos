# libs/controllers/ocorrenciasController.py
from flask import render_template, request, jsonify
from libs.models.create import Create
from libs.models.utils.mock_data import DEVELOPER_MODE
from libs.controllers.decorador import desempenho
from libs.models.modelstate import DadosContexto, OcorrenciasPageViewModel
from libs.models.read import Read # Para manter compatibilidade com self.ocorrencias_read no get_ocorrencias
import json
import time

class OcorrenciasController:
    def __init__(self):
        self.ocorrencias_create = None if DEVELOPER_MODE else Create("op_ocorrencia")
        self.ocorrencias_read = None if DEVELOPER_MODE else Read("op_ocorrencia")

    @desempenho
    def get_ocorrencias(self):
        """API: Retorna lista de ocorrências filtradas (GET)"""
        # Mantém a lógica de API separada pois é para AJAX/JSON, 
        # mas idealmente poderia mover para o DadosContexto no futuro.
        try:
            if DEVELOPER_MODE:
                from libs.models.utils.mock_data import get_mock_data
                return jsonify(get_mock_data('op_ocorrencia') or [])
            
            # Filtros via query params
            status_filter = request.args.get('status')
            requer_acao = request.args.get('requer_acao')
            limit = request.args.get('limit', type=int, default=50)
            
            where = {}
            if status_filter:
                lista_status = [s.strip() for s in status_filter.split(',')]
                if len(lista_status) == 1:
                    where['status'] = lista_status[0]
                else:
                    where['status'] = ('IN', lista_status)
            
            if requer_acao is not None:
                val = requer_acao.lower() == 'true'
                where['requer_acao'] = 1 if val else 0
            
            dados = self.ocorrencias_read.where(
                where=where,
                limit=limit,
                order_by='created_at',
                desc=True
            )
            return jsonify(dados)
            
        except Exception as e:
            print(f"[ERRO] get_ocorrencias: {e}")
            return jsonify({"error": str(e)}), 500

    @desempenho
    def ocorrencias_page(self):
        """Renderiza a página de ocorrências usando ViewModel"""
        inicio = time.time()
        # 1. Cria Contexto
        ctx = DadosContexto()
        
        # 2. Carrega ViewModel
        vm = OcorrenciasPageViewModel.carregar(ctx)
        
        fim = time.time()
        print(f"ocorrenciasController.ocorrencias_page - Tempo de execução: {fim - inicio} segundos")
        # 3. Renderiza
        return render_template(
            "ocorrencias.html",
            vm=vm,
            usinas=vm.usinas,
            usuarios=vm.usuarios,
            templates=vm.templates,
            categorias=vm.categorias,
            tipos=vm.tipos
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
                "operador_id": data.get("operador_id", 1),
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
