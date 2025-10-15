import httpx
import time

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

async def get_data(config, data):
    '''config: dict {ip: str, port: int, tipo: str, unidade: str}
       data: dict {conexao: str, registers: dict}'''
    inicio = time.time()
    body = {
        "conexao": data['conexao'],
        "registers": data[config['tipo']]
    }    
    tipo = config['tipo'] if config['tipo'] != 'temperaturas' else 'leituras'
    # Definindo timeout de 3 segundos para a requisição
    timeout = httpx.Timeout(3.0)
    async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
        try:
            response = await client.post(f"http://{config['ip']}:{config['port']}/readCLP/{tipo}", json=body)
            # print("##",5)
            # print('Query: ', f"http://{config['ip']}:{config['port']}/readCLP/{tipo}")
            # print(body)
            
            leituras_data = response.json()
            # print('leituras_data: ', leituras_data)
            # print("##",5)
            fim = time.time() - inicio
            if leituras_data['status'] == 'success':
                
                # print("##",5)
                return leituras_data['data'], fim
            else:
                # print('leituras_data: ', leituras_data)
                # print("##",5)
                raise Exception(f"[ERRO] {leituras_data.get('message')}")
        except (httpx.TimeoutException, Exception) as e:
            print('Erro: ', e)
            fim = time.time() - inicio
            gerar_dados = generate_data(body)
            return gerar_dados, fim