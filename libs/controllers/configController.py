# libs/controllers/configController.py
from flask import render_template, request, jsonify
from datetime import datetime
from libs.models.read import Read
from libs.models.mock_data import DEVELOPER_MODE, get_mock_data
from libs.models.utils.utils import desempenho
from libs.models.readRT import get_data
import json
import os
import asyncio

class ConfigController:
    def __init__(self):
        self.usinas = None if DEVELOPER_MODE else Read("op_usina")
        self.config_file_path = "config/usinas_dispositivos.json"
    
    @desempenho
    def config_page(self):
        """Renderiza a página de configuração"""
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            usinas = get_mock_data('op_usina')
        else:
            # Usa dados reais do banco de dados
            usinas = self.usinas.get_all()
        return render_template("configuracoes.html", usinas=usinas)
    
    @desempenho
    def salvar_configuracao(self):
        """Salva a configuração de usinas e dispositivos"""
        try:
            config_data = request.get_json()
            
            if not config_data:
                return jsonify({"error": "Nenhum dado foi enviado"}), 400
            
            # Validação básica
            if not isinstance(config_data, dict):
                return jsonify({"error": "Formato de dados inválido"}), 400
            
            # Validar estrutura de cada usina
            for usina_nome, usina_data in config_data.items():
                if not isinstance(usina_data, dict):
                    return jsonify({"error": f"Dados inválidos para a usina {usina_nome}"}), 400
                
                # Verificar campos obrigatórios da usina
                if 'ip' not in usina_data or 'port' not in usina_data:
                    return jsonify({"error": f"IP e porta são obrigatórios para a usina {usina_nome}"}), 400
                
                # Verificar se tem pelo menos um dispositivo
                if 'dispositivos' not in usina_data or not usina_data['dispositivos']:
                    return jsonify({"error": f"A usina {usina_nome} precisa ter pelo menos um dispositivo"}), 400
                
                # Validar cada dispositivo
                for disp_nome, disp_data in usina_data['dispositivos'].items():
                    if not isinstance(disp_data, dict):
                        return jsonify({"error": f"Dados inválidos para o dispositivo {disp_nome}"}), 400
                    
                    # Verificar campos obrigatórios do dispositivo
                    if 'conexao' not in disp_data:
                        return jsonify({"error": f"Conexão é obrigatória para o dispositivo {disp_nome}"}), 400
                    
                    if 'ip' not in disp_data['conexao'] or 'port' not in disp_data['conexao']:
                        return jsonify({"error": f"IP e porta são obrigatórios para o dispositivo {disp_nome}"}), 400
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            
            # Salvar configuração em arquivo JSON
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                "success": True,
                "message": "Configuração salva com sucesso",
                "usinas_count": len(config_data)
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @desempenho
    def carregar_configuracao(self):
        """Carrega a configuração salva"""
        try:
            if not os.path.exists(self.config_file_path):
                return jsonify({"error": "Nenhuma configuração encontrada"}), 404
            
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return jsonify(config_data), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    async def testar_leitura_async(self, data):
        """Testa a leitura de uma variável do CLP"""
        try:
            entrada_id = data.get('entrada_id')
            usina = data.get('usina')
            dispositivo = data.get('dispositivo')
            variavel = data.get('variavel')
            tipo_secao = data.get('tipo_secao')
            
            # Preparar configuração para a API
            config = {
                'ip': usina['ip'],
                'port': usina['port'],
                'tipo': tipo_secao
            }
            
            # Preparar dados da leitura
            read_data = {
                'conexao': {
                    'ip': dispositivo['ip'],
                    'port': dispositivo['port'],
                    'timeout': 3.0
                },
                tipo_secao: {
                    variavel['tipo']: {
                        variavel['nome']: variavel['endereco']
                    }
                }
            }
            
            # Fazer a leitura
            resultado, tempo = await get_data(config, read_data)
            
            # Verificar se obteve sucesso
            if resultado and variavel['tipo'] in resultado and variavel['nome'] in resultado[variavel['tipo']]:
                valor = resultado[variavel['tipo']][variavel['nome']]
                
                return {
                    'entrada_id': entrada_id,
                    'status': 'success',
                    'nome': variavel['nome'],
                    'tipo': variavel['tipo'],
                    'valor': valor,
                    'tempo': f"{tempo:.3f}s",
                    'message': 'Leitura realizada com sucesso'
                }
            else:
                return {
                    'entrada_id': entrada_id,
                    'status': 'error',
                    'nome': variavel['nome'],
                    'message': 'Variável não encontrada na resposta do CLP'
                }
                
        except Exception as e:
            return {
                'entrada_id': data.get('entrada_id'),
                'status': 'error',
                'nome': data.get('variavel', {}).get('nome', 'desconhecida'),
                'message': str(e)
            }