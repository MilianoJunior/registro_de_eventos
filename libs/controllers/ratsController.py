# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. gerar_pdf_bytes → gera PDF em bytes via WeasyPrint
# 2. caminho_absoluto_projeto → resolve caminho absoluto no projeto
# 3. caminho_pdf → converte caminho relativo em file://
# 4. RatsController.__init__ → injeta modelos e contexto
# 5. RatsController.save_base64_image → salva imagem base64 no assets/RAT
# 6. RatsController.inforat → lista RATs e KPIs
# 7. RatsController.criarrat → carrega formulário de criação
# 8. RatsController.salvarrat → cria RAT e itens associados
# 9. RatsController.upload_foto → upload de foto isolada
# 10. RatsController.ver_rat → consulta RAT detalhada
# 11. RatsController.buscar_produtos → busca produtos por termo
# 12. RatsController.modificarrat → carrega edição de RAT
# 13. RatsController.gerarprotocolo → gera protocolo sequencial
# 14. RatsController.atualizar_rat → atualiza RAT e itens
# 15. RatsController.atualizar_status_financeiro → altera status financeiro
# 16. RatsController.deletar_rat → exclui RAT e arquivos
# 17. RatsController.gerar_pdf → gera PDF de RAT
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# CONFIGURACOES, CONSTANTES E MAPAS
# -------------------------------------------------------------------

import os
import base64
import json
import uuid
from datetime import datetime
from flask import render_template, request, make_response
from werkzeug.utils import secure_filename
from weasyprint import HTML
from libs.models.modelstate import DadosContexto
from libs.models.rats_crud import Clientes, Usuarios, Rat, RatServicos, RatMateriais, RatFotos, Produtos
from libs.models.utils.utils import format_date_br, format_time_hm, format_float_hours, format_duration_str

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
RAT_DIR = os.path.join(ASSETS_DIR, 'RAT')
LOGO_PATH = f"file://{os.path.join(ASSETS_DIR, 'logo.png')}"


def caminho_absoluto_projeto(caminho_relativo):
    if not caminho_relativo:
        return ""
    if caminho_relativo.startswith('/assets/') or caminho_relativo.startswith('assets/'):
        caminho_relativo = caminho_relativo.lstrip('/')
        return os.path.join(BASE_DIR, caminho_relativo)
    if os.path.isabs(caminho_relativo):
        return caminho_relativo
    caminho_relativo = caminho_relativo.lstrip('/')
    return os.path.join(BASE_DIR, caminho_relativo)


def caminho_pdf(caminho_relativo):
    caminho = caminho_absoluto_projeto(caminho_relativo)
    return f"file://{caminho}" if caminho else ""


def gerar_pdf_bytes(html_content, base_url=None):
    try:
        pdf_file = HTML(string=html_content, base_url=base_url).write_pdf()
        return pdf_file
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        raise

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
            _, encoded = base64_str.split(",", 1)
            data = base64.b64decode(encoded)
            save_dir = os.path.join(RAT_DIR, subfolder)
            
            # Garantir existência e tentar ajustar permissões
            if not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
                try:
                    os.chmod(save_dir, 0o777) # Tenta permissão total se criou agora
                except Exception:
                    pass

            file_path = os.path.join(save_dir, filename)
            
            # Salvar arquivo
            with open(file_path, "wb") as f:
                f.write(data)
            
            # Ajustar permissões do arquivo criado
            try:
                os.chmod(file_path, 0o666)
            except Exception:
                pass

            return f"/assets/RAT/{subfolder}/{filename}"
        except OSError as e:
            import getpass
            current_user = getpass.getuser()
            uid = os.getuid()
            gid = os.getgid()
            debug_info = f"User: {current_user} (UID: {uid}, GID: {gid})"
            
            print(f"[ERRO PERMISSÃO] {debug_info} - Falha ao salvar imagem {filename}: {e}")
            
            # Levantar exceção detalhada com o usuário real que está rodando o script
            raise Exception(f"Erro de Permissão: O usuário do sistema '{current_user}' não tem permissão de escrita na pasta assets. Execute no terminal: sudo chmod -R 777 /opt/cog/registro_de_eventos/assets")
        except Exception as e:
            print(f"[ERRO GERAL] Falha ao salvar imagem {filename}: {e}")
            raise Exception(f"Erro ao processar imagem: {str(e)}")

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
                total_pages=total_pages,
                search_query=search_query
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
        try:
            if 'file' not in request.files:
                return {'status': 'error', 'message': 'Nenhum arquivo enviado'}, 400
            file = request.files['file']
            if file.filename == '':
                return {'status': 'error', 'message': 'Nenhum arquivo selecionado'}, 400
            if file:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Certificar que RAT_DIR e imgs existem
                upload_folder = os.path.join(RAT_DIR, 'imgs')
                
                # Debug para logs do servidor
                print(f"[UPLOAD] Tentando salvar em: {upload_folder}")

                if not os.path.exists(upload_folder):
                    try:
                        os.makedirs(upload_folder, exist_ok=True)
                        print(f"[UPLOAD] Diretório criado: {upload_folder}")
                    except OSError as e:
                        print(f"[UPLOAD] Erro ao criar diretório: {e}")
                        return {'status': 'error', 'message': f'Erro de permissão ao criar pasta: {str(e)}'}, 500

                file_path = os.path.join(upload_folder, unique_filename)
                
                try:
                    file.save(file_path)
                    print(f"[UPLOAD] Arquivo salvo: {file_path}")
                except Exception as e:
                    print(f"[UPLOAD] Erro ao salvar arquivo: {e}")
                    return {'status': 'error', 'message': f'Erro ao gravar arquivo: {str(e)}'}, 500

                relative_path = f"/assets/RAT/imgs/{unique_filename}"
                return {'status': 'success', 'url': relative_path}, 200
                
        except Exception as e:
            print(f"[UPLOAD] Erro inesperado: {e}")
            return {'status': 'error', 'message': f'Erro interno: {str(e)}'}, 500

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
            print(f"Modificando RAT: {rat_id}")
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

            servicos = data.get('servicos', [])
            tecnico_id = None
            if servicos:
                exec_val = servicos[0].get('executante')
                if exec_val:
                    tecnico_id = int(exec_val)

            # 1. Atualizar RAT (Informações Descritivas)
            rat_update = {
                'descricao_atividades': data.get('descricao_atividades'),
                'conclusao': data.get('conclusao'),
                'deslocamento': data.get('deslocamento'),
                'tecnico_id': tecnico_id
            }
            self.rat_model.update(rat_update, where=f"id = {rat_id}")

            # 2. Atualizar Serviços (Delete all for RAT and Re-insert)
            self.rat_servicos_model.delete(where=f"rat_id = {rat_id}")
            
            if servicos:
                for svc in servicos:
                    # Validate mandatory fields
                    if svc.get('data') and svc.get('inicio') and svc.get('fim'):
                        executante_val = svc.get('executante')
                        self.rat_servicos_model.create({
                            'rat_id': rat_id,
                            'data_servico': svc['data'],
                            'hora_inicio': svc['inicio'],
                            'hora_fim': svc['fim'],
                            'executante_id': int(executante_val) if executante_val else None
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
                paths = self.rat_fotos_model.read(['caminho_arquivo'], where=f"id IN ({ids_str})")
                for p in paths:
                    try:
                        full_path = caminho_absoluto_projeto(p.get('caminho_arquivo'))
                        if full_path and os.path.exists(full_path):
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

            status_permitidos = ['nao_faturavel', 'pendente_faturamento', 'aguardando_pagamento', 'liquidado', 'inadimplente']
            if novo_status not in status_permitidos:
                return {'message': 'Status inválido'}, 400

            sucesso = self.rat_model.update({'status_financeiro': novo_status},where=f"id = {rat_id}")

            if sucesso:
                return {'message': 'Status atualizado com sucesso'}, 200
            
            return {'message': 'Erro ao atualizar status'}, 500

        except Exception as e:
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
                    full_path = caminho_absoluto_projeto(photo.get('caminho_arquivo'))
                    if full_path and os.path.exists(full_path):
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
                            full_path = caminho_absoluto_projeto(rat_data.get(key))
                            if full_path and os.path.exists(full_path):
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

            rat['data_emissao_formatada'] = format_date_br(rat.get('data_emissao', ''))
            
            total_seconds_rat = 0
            
            for svc in servicos:
                svc['data_servico_formatada'] = format_date_br(svc.get('data_servico', ''))

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
                             diff_mins = 0
                        
                        total_seconds_rat += diff_mins * 60
                        
                        dh = diff_mins // 60
                        dm = diff_mins % 60
                        tempo_decorrido = f"{dh:02d}:{dm:02d}"
                        
                    except Exception as e:
                        print(f"Erro calculo horas: {e}")
                
                svc['tempo_decorrido'] = tempo_decorrido

            total_hours_float = total_seconds_rat / 3600
            rat['total_horas'] = format_float_hours(total_hours_float)

            rat['caminho_assinatura_tec_absoluto'] = caminho_pdf(rat.get('caminho_assinatura_tec'))
            rat['caminho_assinatura_cli_absoluto'] = caminho_pdf(rat.get('caminho_assinatura_cli'))

            for foto in fotos:
                foto['caminho_absoluto'] = caminho_pdf(foto.get('caminho_arquivo'))

            html = render_template(
                'components/_pdf_rats.html',
                rat=rat,
                servicos=servicos,
                materiais=materiais,
                fotos=fotos,
                logo_path=LOGO_PATH
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

