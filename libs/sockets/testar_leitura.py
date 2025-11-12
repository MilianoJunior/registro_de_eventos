"""Handlers para eventos Socket.IO relacionados a testes de leitura."""

import asyncio
from flask_socketio import emit

from libs.servicos.readRT import get_data


def register_testar_leitura_handler(socketio):
    """Registra o handler do evento 'testar_leitura'."""

    @socketio.on("testar_leitura")
    def handle_testar_leitura(payload):
        """Executa uma leitura de variavel do CLP e retorna o resultado via socket."""
        config = payload.get("config", {})
        data = payload.get("data", {})
        entrada_id = payload.get("entrada_id")
        
        # Extrair informações de contexto (se disponíveis)
        nome_usina = payload.get("nome_usina", "Usina de teste")
        nome_dispositivo = payload.get("nome_dispositivo", "Dispositivo de teste")

        print("[SOCKET] Recebido pedido de teste:")
        print(f"   Unidade: {config.get('unidade')}")
        print(f"   Tipo: {config.get('tipo')}")

        try:
            # Executar funcao assinc em thread separada
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resultado, tempo = loop.run_until_complete(get_data(config, data, nome_usina, nome_dispositivo))
            loop.close()

            print(f"[SOCKET] Resultado da API: {resultado}")

            if resultado:
                for tipo_dado, valores in resultado.items():
                    for nome_var, valor in valores.items():
                        emit(
                            "resultado_teste_leitura",
                            {
                                "entrada_id": entrada_id,
                                "status": "success",
                                "nome": nome_var,
                                "tipo": tipo_dado,
                                "valor": valor,
                                "tempo": f"{tempo:.3f}s",
                                "message": "Leitura realizada com sucesso",
                            },
                        )
                        return

            emit(
                "resultado_teste_leitura",
                {
                    "entrada_id": entrada_id,
                    "status": "error",
                    "nome": "desconhecida",
                    "message": "Nenhum valor retornado pela API",
                },
            )

        except Exception as exc:
            print(f"[SOCKET] Erro ao testar leitura: {exc}")
            import traceback

            traceback.print_exc()
            emit(
                "resultado_teste_leitura",
                {
                    "entrada_id": entrada_id,
                    "status": "error",
                    "nome": "desconhecida",
                    "message": f"Erro: {exc}",
                },
            )
