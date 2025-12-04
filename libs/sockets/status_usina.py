import json
import time
from typing import Any, Dict
try:  # pragma: no cover - fallback para ambientes sem flask_socketio
    from flask_socketio import emit
except ImportError:  # pragma: no cover
    emit = None  # type: ignore

from libs.servicos.coletor_core import coletar_status_completo, get_dados_cache, registrar_intervencao


# -------------------------------------------------------------------
# FLUXO DO MÓDULO (Socket.IO Handler)
# 1. _1_register_status_usina_handler → registra handler socket.io
# 2. _2_handle_status_usinas → recebe evento do frontend
# 3. _3_handle_registrar_intervencao → recebe comando de intervenção
# 4. get_dados_cache → busca cache ou chama coletor_core
# 5. coletar_status_completo → (em coletor_core.py)
# 6. emit → envia para frontend
# 
# OBS: Salvamento no banco é feito pela thread em main.py
# -------------------------------------------------------------------

def _1_register_status_usina_handler(socketio):
    # print('--------------------------------'*2)
    # print("Registrando handler socket.io para 'solicitar_status_usinas'")
    contador_solicitacoes = {"total": 0, "ultima_timestamp": 0}

    @socketio.on("solicitar_status_usinas")
    def _2_handle_status_usinas(_payload=None):
        # print('--------------------------------'*2)
        # print("Recebendo evento 'solicitar_status_usinas'")
        inicio_tempo = time.time()
        contador_solicitacoes["total"] += 1
        contador_solicitacoes["ultima_timestamp"] = time.time()

        # Usa cache compartilhado (evita coleta duplicada se thread acabou de executar)
        # Agora usamos o estado global de intervenções dentro do coletor_core, 
        # então não precisamos passar argumentos extras.
        payload = get_dados_cache("coleta_completa", coletar_status_completo)

        # Log compacto
        for usina in payload.get("usinas", []):
            # print(f"Usina: {usina['nome']} ({usina['slug']})")
            dispositivos = usina.get("dispositivos", {})
            # for nome_disp, disp in dispositivos.items():
            #     print(f"  Dispositivo: {nome_disp}")
            #     print(f"    descricao: {disp.get('descricao')}")
            #     print(f"    potencia_ativa_mw: {disp.get('potencia_ativa_mw')}")
            #     print(f"    erro: {disp.get('erro')}")
            # print("-" * 50)

        try:
            emit("status_usinas_dados", payload, broadcast=True)
            # print('Finalizado em ', time.time() - inicio_tempo, ' segundos')
            # print('✅ [SOCKET][status_usina] Evento "status_usinas_dados" emitido com sucesso!')
            # print('--------------------------------'*2)
        except Exception as e:
            print(f'❌ [SOCKET][status_usina] ERRO ao emitir evento: {e}')

    @socketio.on("registrar_intervencao_status")
    def _3_handle_registrar_intervencao(payload):
        """
        Recebe solicitação do frontend para registrar intervenção manual.
        Payload esperado: {
            'usina': 'slug',
            'dispositivo': 'UG-XX',
            'motivo': 'MANUTENCAO' | 'RESTRICAO' | 'NORMAL'
        }
        """
        if not payload or not isinstance(payload, dict):
            return
        
        usina = payload.get('usina')
        dispositivo = payload.get('dispositivo')
        motivo = payload.get('motivo')
        
        if usina and dispositivo and motivo:
            print(f"📝 [SOCKET] Registrando intervenção: {usina}/{dispositivo} -> {motivo}")
            registrar_intervencao(usina, dispositivo, motivo)
            
            # Força uma atualização imediata para refletir a mudança para todos
            # Invalida cache se necessário ou apenas emite novo status
            # Como get_dados_cache tem TTL, podemos chamar o handler principal para tentar emitir
            # Se quisermos imediato, talvez limpar o cache ou chamar coletar_status_completo direto
            
            # Opção simples: chama o handler de status para atualizar a tela
            _2_handle_status_usinas()

__all__ = [
    "_1_register_status_usina_handler",
]
