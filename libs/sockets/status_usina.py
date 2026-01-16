import json
import time
from typing import Any, Dict
try:  # pragma: no cover - fallback para ambientes sem flask_socketio
    from flask_socketio import emit, join_room, leave_room
except ImportError:  # pragma: no cover
    emit = None  # type: ignore
    join_room = None  # type: ignore
    leave_room = None  # type: ignore

from libs.servicos.coletor_core import coletar_status_completo, get_dados_cache, registrar_intervencao


# -------------------------------------------------------------------
# FLUXO DO MÓDULO (Socket.IO Handler)
# 1. _1_register_status_usina_handler → registra handler socket.io
# 2. _2_handle_status_usinas → (home) emite payload completo (broadcast)
# 3. _3_handle_entrar_usina_room → entra no room da usina (usina:<slug>)
# 4. _4_handle_sair_usina_room → sai do room da usina
# 5. _5_handle_status_usina → (usinas) emite payload mínimo por usina (room)
# 6. _6_handle_registrar_intervencao → recebe comando de intervenção
# 7. _extrair_payload_usina_minimo → reduz payload para 1 usina (potência por UG)
# 8. get_dados_cache → busca cache ou chama coletor_core
# 9. coletar_status_completo → (em coletor_core.py)
# 10. emit → envia para frontend
# 
# OBS: Salvamento no banco é feito pela thread em main.py
# -------------------------------------------------------------------

def _extrair_payload_usina_minimo(payload: Dict[str, Any], usina_slug: str) -> Dict[str, Any]:
    if not payload or not isinstance(payload, dict):
        return {"success": False, "slug": usina_slug, "error": "payload_invalido"}

    usina = next((u for u in (payload.get("usinas") or []) if (u or {}).get("slug") == usina_slug), None)
    if not usina:
        return {"success": False, "slug": usina_slug, "error": "usina_nao_encontrada"}

    dispositivos = usina.get("dispositivos") or {}
    potencia_por_dispositivo: Dict[str, Any] = {}
    total_mw = 0.0

    for nome, disp in dispositivos.items():
        mw = (disp or {}).get("potencia_ativa_mw")
        if isinstance(mw, (int, float)):
            potencia_por_dispositivo[str(nome)] = float(mw)
            total_mw += float(mw)
        else:
            potencia_por_dispositivo[str(nome)] = None

    return {
        "success": bool(payload.get("success")),
        "slug": usina_slug,
        "timestamp": payload.get("timestamp"),
        "potencia_total_mw": total_mw,
        "potencia_por_dispositivo": potencia_por_dispositivo,
    }

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
            print(f"📝 [SOCKET] Emitindo status_usinas_dados para todos as usinas") 
            emit("status_usinas_dados", payload, broadcast=True)
            print(f"📝 [SOCKET] status_usinas_dados emitido com sucesso para todos as usinas")
            print('Finalizado em ', time.time() - inicio_tempo, ' segundos')
            # print('✅ [SOCKET][status_usina] Evento "status_usinas_dados" emitido com sucesso!')
            # print('--------------------------------'*2)
        except Exception as e:
            print(f'❌ [SOCKET][status_usina] ERRO ao emitir evento: {e}')

    @socketio.on("entrar_usina_room")
    def _3_handle_entrar_usina_room(payload):
        if not join_room or not payload or not isinstance(payload, dict):
            return
        usina = (payload.get("usina") or "").strip()
        if not usina:
            return
        print(f"📝 [SOCKET] Entrando no room da usina: {usina}")    
        join_room(f"usina:{usina}")

    @socketio.on("sair_usina_room")
    def _4_handle_sair_usina_room(payload):
        if not leave_room or not payload or not isinstance(payload, dict):
            return
        usina = (payload.get("usina") or "").strip()
        if not usina:
            return
        print(f"📝 [SOCKET] Saindo do room da usina: {usina}")
        leave_room(f"usina:{usina}")

    @socketio.on("solicitar_status_usina")
    def _5_handle_status_usina(payload):

        inicio_tempo = time.time()
        if not payload or not isinstance(payload, dict):
            return
        usina = (payload.get("usina") or "").strip()
        if not usina:
            return

        payload_full = get_dados_cache("coleta_completa", coletar_status_completo)
        payload_min = _extrair_payload_usina_minimo(payload_full, usina)

        try:
            print(f"📝 [SOCKET] Emitindo status_usina_dados para a usina: {usina}")
            emit("status_usina_dados", payload_min, room=f"usina:{usina}")
            print(f"📝 [SOCKET] status_usina_dados emitido com sucesso para a usina: {usina}")
            print('Finalizado em ', time.time() - inicio_tempo, ' segundos')
        except Exception as e:
            print(f'❌ [SOCKET][status_usina] ERRO ao emitir status_usina_dados: {e}')

    @socketio.on("registrar_intervencao_status")
    def _6_handle_registrar_intervencao(payload):
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

