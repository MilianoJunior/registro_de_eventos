import os
import json
import google.generativeai as genai
from flask_socketio import emit

def register_ai_generation_handler(socketio):
    @socketio.on('gerar_relatorio_ia')
    def handle_ai_generation(data):
        print(f"📝 [SOCKET] Recebendo solicitação de IA: {data.get('cliente_nome', 'Cliente')}")
        
        relato = data.get('relato_cliente', 'Não informado')
        servicos = data.get('servicos', []) # Lista de {data, inicio, fim, executante, observacao}
        materiais = data.get('materiais', []) # Lista de {descricao, quantidade, unidade}
        deslocamento = data.get('deslocamento', 'Não informado')
        tipo_atividade = data.get('tipo_atividade', 'Manutenção')
        
        # Formatar serviços para o prompt
        servicos_txt = ""
        for s in servicos:
            obs = f" - Obs: {s.get('observacao')}" if s.get('observacao') else ""
            servicos_txt += f"- Dia {s.get('data')} ({s.get('inicio')} às {s.get('fim')}): Atividade técnica realizada{obs}\n"

        # Formatar materiais
        materiais_txt = "\n".join([f"- {m.get('quantidade')} {m.get('unidade')} de {m.get('descricao')}" for m in materiais])
        if not materiais_txt: materiais_txt = "Nenhum material registrado."

        prompt = f"""
        Você é um Assistente Técnico Especialista da empresa Engesep, focado em manutenção de usinas e automação.
        Sua tarefa é redigir um RELATÓRIO TÉCNICO PROFISSIONAL baseado nos dados brutos do atendimento.

        DADOS DO ATENDIMENTO:
        - Tipo: {tipo_atividade}
        - Defeito/Solicitação (Cliente): {relato}
        - Deslocamento: {deslocamento}
        
        SERVIÇOS REGISTRADOS (Horas):
        {servicos_txt}

        MATERIAIS APLICADOS:
        {materiais_txt}

        INSTRUÇÕES:
        1. Gere um texto para o campo 'Descrição das Atividades'. Seja técnico, formal e direto. Descreva as ações cronologicamente ou logicamente. Se houver pouca informação nos serviços, infira procedimentos padrão de {tipo_atividade} coerentes com o relato do problema, mas não invente dados específicos. Mencione o uso dos materiais se fizer sentido.
        2. Gere um texto para o campo 'Conclusão'. Indique se o equipamento/sistema foi restabelecido, se está em observação ou se restaram pendências (baseado no contexto).
        
        FORMATO DE SAÍDA (Apenas JSON):
        {{
            "descricao": "Texto completo da descrição...",
            "conclusao": "Texto da conclusão..."
        }}
        """
        
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                # Fallback check for user specific key file if env var not set, or error
                # For this environment, we might rely on the user having it set.
                emit('erro_ia', {'message': 'Configuração de IA ausente (GEMINI_API_KEY).'})
                return

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3-flash-preview') # Usar gemini-pro como fallback mais compativel
            
            # Set generation config to force JSON if possible or rely on prompt
            response = model.generate_content(prompt)
            
            text_response = response.text
            # Limpeza básica de Markdown caso a IA retorne ```json ... ```
            if "```json" in text_response:
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif "```" in text_response:
                text_response = text_response.split("```")[1].strip()
            
            try:
                result = json.loads(text_response)
                emit('relatorio_gerado_sucesso', result)
            except json.JSONDecodeError:
                # Fallback se não for JSON válido
                emit('relatorio_gerado_sucesso', {
                    'descricao': text_response, 
                    'conclusao': 'Verificar texto gerado na descrição.'
                })
                
        except Exception as e:
            print(f"❌ Erro na geração IA: {e}")
            emit('erro_ia', {'message': f'Falha ao gerar relatório: {str(e)}'})
