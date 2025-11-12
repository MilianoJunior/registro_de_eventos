import httpx
import time
from libs.controllers.decorador import desempenho

LEITURA_ATIVA = {}
contador_leituras = 0

async def list_modbus_connections(config):
    """Lista todas as conexões Modbus ativas via API."""
    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(5.0)) as client:
        try:
            response = await client.get(f"http://{config['ip']}:{config['port']}/listConnections")
            connections_data = response.json()
            if connections_data.get('status') != 'success':
                await close_modbus_connections(config)
                raise Exception(f"[ERRO API] {connections_data.get('message')}")
            return connections_data.get('data'), time.time()
        except Exception as e:
            await close_modbus_connections(config)
            raise Exception(f"[ERRO] {e}")
        
async def close_modbus_connections(config):
    """Fecha todas as conexões Modbus ativas via API."""
    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(5.0)) as client:
        try:
            response = await client.post(f"http://{config['ip']}:{config['port']}/closeConnections")
            connections_data = response.json()
            if connections_data.get('status') != 'success':
                raise Exception(f"[ERRO API] {connections_data.get('message')}")
            return True
        except Exception as e:
            raise Exception(f"[ERRO] {e}")

# @desempenho
async def get_data(config, data, nome_usina=None, nome_dispositivo=None):
    '''config: dict {ip: str, port: int, tipo: str, unidade: str}
       data: dict {conexao: dict, registers: dict} ou {conexao: dict, leituras/alarmes/temperaturas: dict}
       nome_usina: str (opcional) - Nome da usina para contexto nas mensagens de erro
       nome_dispositivo: str (opcional) - Nome do dispositivo para contexto nas mensagens de erro
       
       Formato esperado do data (novo formato da API):
       {
         "conexao": {"ip": "192.168.0.10", "port": 502, "timeout": 10.0},
         "registers": {
           "nivel_montante": [13519, "REAL", {"offset": -1, "converter": "word_order"}],
           "potencia_ativa": [13407, "INT", {"offset": -1}],
           "religamento": [12321, "BOOLEAN", {"offset": -1}]
         }
       }
       
       Formato antigo (retrocompatibilidade):
       {
         "conexao": {"ip": "192.168.0.10", "port": 502, "timeout": 10.0},
         "leituras": {
           "BOOLEAN": {"var1": [addr, "BOOLEAN", {...}], ...}
         }
       }
    '''
    global contador_leituras  # Declarar como global antes de usar
    
    inicio = time.time()
    tipo = config['tipo'] if config['tipo'] != 'temperaturas' else 'leituras'
    
    # Converter formato antigo para novo formato se necessário
    registers = data.get('registers')
    if registers is None:
        # Formato antigo: data[config['tipo']] contém {"TIPO": {nome: [addr, tipo, opts]}}
        tipo_dados = data.get(config['tipo'], {})
        registers = {}
        
        # Achatar a estrutura agrupada por tipo para um único dicionário
        for tipo_dado, vars_dict in tipo_dados.items():
            if isinstance(vars_dict, dict):
                registers.update(vars_dict)
    
    body = {
        "conexao": data['conexao'],
        "registers": registers
    }
    
    # Informações de conexão do CLP
    ip_clp = data['conexao']['ip']
    port_clp = data['conexao']['port']
    
    # Monta contexto para mensagens de erro
    contexto = ""
    if nome_usina:
        contexto = f"[{nome_usina}"
        if nome_dispositivo:
            contexto += f" - {nome_dispositivo}"
        contexto += "] "
    
    # Definindo timeout de 3 segundos para a requisição
    timeout = httpx.Timeout(3.0)
    if LEITURA_ATIVA.get(config['ip'], False):
        contador_leituras += 1
        print(f"    {contador_leituras}ª Leitura rejeitada, outra leitura ativa para o IP: {config['ip']}")
        return None, 0
    LEITURA_ATIVA[config['ip']] = True
    async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
        try:
            print("##"*5)
            
            print('Query: ', f"http://{config['ip']}:{config['port']}/readCLP/{tipo}")
            print('body: ', body)
            response = await client.post(f"http://{config['ip']}:{config['port']}/readCLP/{tipo}", json=body)
            
            leituras_data = response.json()
            print('leituras_data: ', leituras_data)
            print("##"*5)
            fim = time.time() - inicio
            if leituras_data['status'] == 'success':
                # A nova API retorna {nome_var: valor}
                # Precisamos agrupar por tipo para manter retrocompatibilidade
                resultado_api = leituras_data['data']
                
                # Agrupar resultado por tipo de dado baseado nos registers enviados
                resultado_agrupado = {}
                for nome_var, valor in resultado_api.items():
                    # Encontrar o tipo do registrador nos dados enviados
                    if nome_var in registers:
                        tipo_dado = registers[nome_var][1] if len(registers[nome_var]) > 1 else "UNKNOWN"
                        if tipo_dado not in resultado_agrupado:
                            resultado_agrupado[tipo_dado] = {}
                        resultado_agrupado[tipo_dado][nome_var] = valor
                
                return resultado_agrupado, fim
            else:
                # print('leituras_data: ', leituras_data)
                # print("##",5)
                raise Exception(f"[ERRO] {contexto}{leituras_data.get('message')}")
        except httpx.TimeoutException as e:
            print(f'Erro:  {contexto}[ERRO] Timeout ao conectar em {ip_clp}:{port_clp}')
            raise Exception(f"[ERRO] {contexto}Timeout ao conectar em {ip_clp}:{port_clp}")
        except httpx.ConnectError as e:
            print(f'Erro:  {contexto}[ERRO] Falha ao conectar em {ip_clp}:{port_clp}')
            raise Exception(f"[ERRO] {contexto}Falha ao conectar em {ip_clp}:{port_clp}")
        except Exception as e:
            erro_str = str(e)
            # Se já tiver contexto, não duplicar
            if not erro_str.startswith(f"[ERRO] {contexto}"):
                print(f'Erro:  {contexto}[ERRO] {erro_str}')
                raise Exception(f"[ERRO] {contexto}{erro_str}")
            else:
                print(f'Erro:  {erro_str}')
                raise
        finally:
            LEITURA_ATIVA[config['ip']] = False