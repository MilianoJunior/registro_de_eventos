import os
import ast

cont = 0
total_linhas = 0
count = 0



def estrutura_pastas_arquivos(caminho, prefixo="", imprimir=False):
    """
    Função recursiva que imprime o nome das pastas e o código dos arquivos Python, HTML, CSS e JavaScript encontrados.
    :param caminho: Caminho do diretório a ser listado.
    :param prefixo: Prefixo para formatação da saída.
    """
    global cont, total_linhas, count

    for item in os.listdir(caminho):
        item_path = os.path.join(caminho, item)
        list_exclude = ['__pycache__', '.idea', 'README.md', 'requirements.txt', 'prompt.py','__init__.py',
                        'socket.io.js','tests','.git','.cursor','test.py','amv','docs','testes','analise_relatorios.html','analiseController.py']
        list_include = ['.html', '.css', '.js','.yaml','.py','.json']
        list_imprimir = ['.py','.html','.css','.js','.yaml','.json']
        if item in list_exclude:
            continue

        if os.path.isdir(item_path):
            # Se o item é uma pasta, imprime o nome da pasta e faz a chamada recursiva
            cont += 1
            if not imprimir:
                print(f"{prefixo}{item}/")
            estrutura_pastas_arquivos(item_path, prefixo + "    ├── ", imprimir)
        elif os.path.isfile(item_path) and any([item.endswith(ext) for ext in list_include]):
            # Se o item é um arquivo Python, HTML, CSS ou JavaScript, imprime o nome do arquivo
            cont += 1
            if not imprimir:
                print(f"{prefixo}{item}")
                # print(f"{prefixo}├── {item}")
            if imprimir and any([item.endswith(ext) for ext in list_imprimir]):
                try:
                    with open(item_path, 'r', encoding='utf-8') as arquivo:
                        conteudo = arquivo.read()
                        count += 1
                        print('¨¨' * 50)
                        print(f'{count} - Conteúdo do arquivo {item}:')
                        print('¨¨' * 50)
                        print(conteudo)
                        total_linhas += len(conteudo.splitlines())
                        print(f'Quantidade de linhas do arquivo {item}: {len(conteudo.splitlines())} totalizando {total_linhas} linhas.')
                except UnicodeDecodeError:
                    try:
                        with open(item_path, 'r', encoding='latin1') as arquivo:
                            conteudo = arquivo.read()
                            count += 1
                            print('¨¨' * 50)
                            print(f'{count} - Conteúdo do arquivo {item}:')
                            print('¨¨' * 50)
                            print(conteudo)
                            total_linhas += len(conteudo.splitlines())
                            print(f'Quantidade de linhas do arquivo {item}: {len(conteudo.splitlines())} totalizando {total_linhas} linhas.')
                    except Exception as e:
                        print(f"Erro ao ler o arquivo {item}: {str(e)}")

def metodos_arquivos(caminho, prefixo=""):
    """
    Função recursiva que imprime os nomes das pastas e arquivos encontrados, e os métodos dos arquivos Python.
    """
    for item in os.listdir(caminho):
        item_path = os.path.join(caminho, item)

        list_exclude = ['__pycache__', '.idea', 'README.md', 'requirements.txt', 'prompt.py', '__init__.py',
                        'socket.io.js','tests','amv']
        list_include = ['.py', '.html', '.css', '.js']
        list_imprimir = ['.py']
        if item in list_exclude:
            continue

        if os.path.isdir(item_path):
            print(f"{prefixo}{item}/")
            metodos_arquivos(item_path, prefixo + "    ├── ")
        elif os.path.isfile(item_path) and any([item.endswith(ext) for ext in list_imprimir]):
            print(f"{prefixo}{item}")
            with open(item_path, 'r') as arquivo:
                conteudo = arquivo.read()
                tree = ast.parse(conteudo)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        print(f"{prefixo}    ├── Função: {node.name}")
                    elif isinstance(node, ast.ClassDef):
                        print(f"{prefixo}    ├── Classe: {node.name}")
                        for sub_node in node.body:
                            if isinstance(sub_node, ast.FunctionDef):
                                print(f"{prefixo}        ├── Método: {sub_node.name}")



def listar_bibliotecas(caminho):
    """
    Função que retorna todas as bibliotecas importadas nos arquivos Python do projeto.
    """
    bibliotecas = set()

    for root, _, files in os.walk(caminho):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=file_path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    bibliotecas.add(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                bibliotecas.add(node.module)
                    except SyntaxError:
                        print(f"Erro de sintaxe no arquivo: {file_path}")

    return bibliotecas

# Caminho do diretório do projeto
# caminho_projeto = os.getcwd()
# bibliotecas = listar_bibliotecas(caminho_projeto)
# print("Bibliotecas importadas no projeto:")
# for biblioteca in sorted(bibliotecas):
#     print(biblioteca)

# print('--' * 50)
# print('Estutura de pastas e arquivos do diretório atual:')
# print('--' * 50)
path = os.getcwd()
# # Execute the function to create the project structure
# # create_project_structure(path)
#
# estrutura_pastas_arquivos(path, "")
estrutura_pastas_arquivos(path, "")
print('-' * 50)
estrutura_pastas_arquivos(path, "", imprimir=True)
# print('-' * 50)
# print('Métodos e funções dos arquivos Python:')

# contador:  57 tempo_atual:  0.22269940376281738 tempo_total:  12.99897837638855  erros:  47 api versão 1
# contador:  57 tempo_atual:  0.12067461013793945 tempo_total:  7.112741470336914  erros:  1 api versão 2
# contador:  57 tempo_atual:  0.1147918701171875 tempo_total:  6.785559177398682 conta:  1 api versão 3
'''
Preciso criar um socket na pasta libs/sockets/ para ler o status operacional de cada usina em tempo real, e atualizar o status operacional de cada usina na
interface web. Devo usar o mesmo caminho do testar_leitura.py para ler o status operacional de cada usina em tempo real.
o endereço do status operacional é registrado na pasta config/usinas_dispositivos.json, de oncde devem ser lidos os endereços para leitura.
em leituras:BOOLEAN:
    "BOOLEAN": {
                "Status U.P. (parada)": 20326,
                "Status U.P.G.M. (pronta para giro mecânico)": 20327,
                "Status U.P.S.(pronta para sincronização)": 20328,
                "Status U.M.D.(sincronizado)": 20329,
                "Status sincronizado": 20330
            }

o status operacional, será atualizada na pagina home.html, na seção Status das Usinas, deve ser atualizado o status operacional de cada usina.
<span class="bg-success/20 text-success text-xs px-2 py-0.5 rounded flex items-center gap-1">
    <span class="w-1.5 h-1.5 rounded-full bg-success"></span>Operando
</span>
{% elif usina.status_operacional == 'manutencao' %}
<span class="bg-warning/20 text-warning text-xs px-2 py-0.5 rounded flex items-center gap-1">
    <span class="w-1.5 h-1.5 rounded-full bg-warning"></span>Manutenção
</span>
{% else %}
<span class="bg-slate-500/20 text-slate-500 text-xs px-2 py-0.5 rounded flex items-center gap-1">
    <span class="w-1.5 h-1.5 rounded-full bg-slate-500"></span>Parada
</span>
{% endif %}

criei o arquivo libs/sockets/status_usina.py para ler o status operacional de cada usina em tempo real, mas precisar ser vinculado ao home.html


'''

'''
Preciso separar o código abaixo em arquivos separados em componentes reutilizáveis mantendo a estilização com fidelidade máxima, a ideia é
separar apenas o componente _sidebar.html e o arquivo base.html. O home.html deve conter o restante.


Dados mock:

--------------------------------
1. usinas
[
 {
    'id': 1,                                                               # OK
    'nome': 'CGH-APARECIDA',                                               # OK
    'sigla': 'APAR',                                                       # OK
    'timezone': 'America/Sao_Paulo',                                       # OK
    'ativo': 1,                                                            # OK
    'status_operacional': 'operando',                                      # 1 Faltante
    'potencia_ativa_mw': 1200,                                             # 2 Faltante
    'mttr': '13h min',                                                     # 3 Faltante
    'alarmes_por_hora': 8.0,                                               # 4 Faltante
    'alarmes_criticos': 0,                                                 # 5 Faltante
    'incidentes_abertos': 0,                                               # 6 Faltante
    'alarmes_atencao': 3,                                                  # 7 Faltante
    'alarmes_inundantes': 0,                                               # 8 Faltante
    'alarmes_oscilantes': 2,                                               # 9 Faltante
    'energia_nao_gerada_mwh': 0,                                           # 10 Faltante
    'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0},      # 11 Faltante
    'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993),      # OK
    'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)}      # OK
 }
]

1. usinas
[
    {
        'id': 1, 
        'nome': 'CGH-APARECIDA', 
        'sigla': 'APAR', 
        'timezone': 'America/Sao_Paulo', 
        'ativo': 1, 
        'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993), 
        'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)
    }
]
variaveis faltantes:
status_operacional
    1. status_operacional: usar a api em tempo real para obter o status operacional de cada UG
    2. potencia_ativa_mw: usar a api em tempo real para obter a potencia ativa de cada UG 
    3. mttr: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o mttr de cada UG
    4. alarmes_por_hora: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes por hora de cada UG
    5. alarmes_criticos: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes criticos de cada UG
    6. incidentes_abertos: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de incidentes abertos
    7. alarmes_atencao: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes de atencao e definir uma classificação de atencao
    8. alarmes_inundantes: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes inundantes
    9. alarmes_oscilantes: cria um metodo para consultar a tabela op_ocorrencia_hist para obter o numero de alarmes oscilantes
    10. energia_nao_gerada_mwh: cria um metodo para consultar a tabela op_ocorrencia_hist para obter a energia nao gerada de cada UG em mwh
    11. distribuicao_prioridade: cria um metodo para consultar a tabela op_ocorrencia para obter a distribuicao de prioridade de cada UG

    tabelas:

    op_ocorrencia {
      BIGINT id PK
      BIGINT usina_id FK
      BIGINT operador_id FK
      VARCHAR tipo            "ex.: Evento, Alarme, Trip"
      VARCHAR categoria       "ex.: Operação/Humano, Elétrica, Hidráulica..."
      VARCHAR unidade         "ex.: UG-01, Vertedouro..."
      VARCHAR tags            "CSV: ex. 'trip, vibração'"
      TEXT   playbook         "texto livre com instruções"
      TEXT   template_texto   "texto-base aplicado"
      LONGTEXT descricao      "descrição detalhada"
      ENUM status             "aberta|em_andamento|resolvida|cancelada"
      ENUM severidade         "baixa|média|alta|crítica"
      ENUM origem             "humano|scada|api|importacao"
      JSON  metadata          "IDs/leituras extras (opcional)"
      DATETIME created_at
      DATETIME updated_at
      DATETIME resolved_at    "nullable"
    }
    
    op_ocorrencia_hist {
      BIGINT id PK
      BIGINT ocorrencia_id FK
      BIGINT usuario_id FK "nullable"
      ENUM acao            "criado|atualizado|status|comentario|anexo"
      TEXT detalhe
      DATETIME created_at
    }

com base nessas informações, preciso resolver o primeiro problema, que é obter os dados da api em tempo real, para isso,
preciso criar uma classe para consultar a api em tempo real no models:

--------------------------------------------------
2. total_ocorrencias
20
--------------------------------------------------
3. recentes
[{'id': 20, 'usina_id': 5, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'PCH-PEDRAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: UG-01 Gerador - Temperatura alta mancal - LNA - Guia - Trip\nResultado: Religamento das unidades UG-01\nObservação: Após verificar que as temperatura estavam dentro dos números aceitavéis e a parada total da unidade geradora, foi possivel fazer o religamento da mesma.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 12, 2, 4), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 55), 'resolved_at': datetime.datetime(2025, 7, 12, 2, 4)}, {'id': 19, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 11, 0, 52), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 54), 'resolved_at': datetime.datetime(2025, 7, 11, 0, 52)}, {'id': 18, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Evento', 'categoria': 'Elétrica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico e eletrico\nCondição: PSA - Disjuntor de linha 52L - Falha de fechamento\nResultado: Religamento das unidades UG-01 e UG-02\nObservação: Após trip das unidades geradora, foi realizadio o fechamento do disjuntor de linha 52L, e o religamento das unidades geradoras.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 10, 22, 15), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 53), 'resolved_at': datetime.datetime(2025, 7, 10, 22, 15)}, {'id': 17, 'usina_id': 5, 'operador_id': 1, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'PCG PEDRAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: UG-01 - Turbina - Bucha Radial 01 - Trip\nResultado: Religamento da unidade UG-01\nObservação: Após trip da unidade geradora, foi feito o religamento', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 10, 18, 23), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 52), 'resolved_at': datetime.datetime(2025, 7, 10, 18, 23)}, {'id': 16, 'usina_id': 3, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Elétrica', 'unidade': 'CGH HOPPEN', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: UG-01 Relé de proteção - Sobretensão Fase e Neutro\nCondição: UG-01 em Trip\nResultado: Religamento da unidade UG-01\nObservação: Após trip da unidade geradora, foi feito o religamento', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 10, 6, 11), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 51), 'resolved_at': datetime.datetime(2025, 7, 10, 6, 11)}, {'id': 15, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 10, 2, 26), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 49), 'resolved_at': datetime.datetime(2025, 7, 10, 2, 26)}, {'id': 14, 'usina_id': 4, 'operador_id': 1, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 9, 19, 40), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 47), 'resolved_at': datetime.datetime(2025, 7, 9, 19, 40)}, {'id': 13, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 9, 3, 5), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 46), 'resolved_at': datetime.datetime(2025, 7, 9, 3, 5)}, {'id': 12, 'usina_id': 5, 'operador_id': 4, 'tipo': 'Trip', 'categoria': 'Operação/Humano', 'unidade': 'PCH-PEDRAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Partir a UG-02 após um TRIP\nCondição: UG02-UHLM - Ausência fluxo de Oleo 04 - Verificar fluxostasto\nResultado: Não é possível partir a UG-02', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 9, 3, 0), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 45), 'resolved_at': datetime.datetime(2025, 7, 9, 3, 0)}, {'id': 11, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 8, 22, 14), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 44), 'resolved_at': datetime.datetime(2025, 7, 8, 22, 14)}]
--------------------------------------------------
4. status
Counter({'resolvida': 18, 'em_andamento': 1, 'aberta': 1})
--------------------------------------------------
5. por_unidade
[('CGH PICADAS ALTAS', 6), ('CGH HOPPEN', 3), ('CGH-APARECIDA', 3), ('CGH-FAE', 3), ('PCH-PEDRAS', 3), ('CGH-PICADAS ALTAS', 1), ('PCG PEDRAS', 1)]
--------------------------------------------------
6. potencia_total_mw
4150
--------------------------------------------------

dados reais:

--------------------------------
1. usinas
[
    {
        'id': 1, 
        'nome': 'CGH-APARECIDA', 
        'sigla': 'APAR', 
        'timezone': 'America/Sao_Paulo', 
        'ativo': 1, 
        'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993), 
        'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)
    }
]
--------------------------------------------------
2. total_ocorrencias
20
--------------------------------------------------
3. recentes
[{'id': 20, 'usina_id': 5, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'PCH-PEDRAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: UG-01 Gerador - Temperatura alta mancal - LNA - Guia - Trip\nResultado: Religamento das unidades UG-01\nObservação: Após verificar que as temperatura estavam dentro dos números aceitavéis e a parada total da unidade geradora, foi possivel fazer o religamento da mesma.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 12, 2, 4), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 55), 'resolved_at': datetime.datetime(2025, 7, 12, 2, 4)}, {'id': 19, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 11, 0, 52), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 54), 'resolved_at': datetime.datetime(2025, 7, 11, 0, 52)}, {'id': 18, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Evento', 'categoria': 'Elétrica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico e eletrico\nCondição: PSA - Disjuntor de linha 52L - Falha de fechamento\nResultado: Religamento das unidades UG-01 e UG-02\nObservação: Após trip das unidades geradora, foi realizadio o fechamento do disjuntor de linha 52L, e o religamento das unidades geradoras.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 10, 22, 15), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 53), 'resolved_at': datetime.datetime(2025, 7, 10, 22, 15)}, {'id': 17, 'usina_id': 5, 'operador_id': 1, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'PCG PEDRAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: UG-01 - Turbina - Bucha Radial 01 - Trip\nResultado: Religamento da unidade UG-01\nObservação: Após trip da unidade geradora, foi feito o religamento', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 10, 18, 23), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 52), 'resolved_at': datetime.datetime(2025, 7, 10, 18, 23)}, {'id': 16, 'usina_id': 3, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Elétrica', 'unidade': 'CGH HOPPEN', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: UG-01 Relé de proteção - Sobretensão Fase e Neutro\nCondição: UG-01 em Trip\nResultado: Religamento da unidade UG-01\nObservação: Após trip da unidade geradora, foi feito o religamento', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 10, 6, 11), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 51), 'resolved_at': datetime.datetime(2025, 7, 10, 6, 11)}, {'id': 15, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 10, 2, 26), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 49), 'resolved_at': datetime.datetime(2025, 7, 10, 2, 26)}, {'id': 14, 'usina_id': 4, 'operador_id': 1, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 9, 19, 40), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 47), 'resolved_at': datetime.datetime(2025, 7, 9, 19, 40)}, {'id': 13, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 9, 3, 5), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 46), 'resolved_at': datetime.datetime(2025, 7, 9, 3, 5)}, {'id': 12, 'usina_id': 5, 'operador_id': 4, 'tipo': 'Trip', 'categoria': 'Operação/Humano', 'unidade': 'PCH-PEDRAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Partir a UG-02 após um TRIP\nCondição: UG02-UHLM - Ausência fluxo de Oleo 04 - Verificar fluxostasto\nResultado: Não é possível partir a UG-02', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 9, 3, 0), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 45), 'resolved_at': datetime.datetime(2025, 7, 9, 3, 0)}, {'id': 11, 'usina_id': 4, 'operador_id': 3, 'tipo': 'Trip', 'categoria': 'Hidráulica', 'unidade': 'CGH PICADAS ALTAS', 'tags': '', 'playbook': None, 'template_texto': None, 'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 'status': 'resolvida', 'severidade': 'alta', 'origem': 'humano', 'metadata': None, 'created_at': datetime.datetime(2025, 7, 8, 22, 14), 'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 44), 'resolved_at': datetime.datetime(2025, 7, 8, 22, 14)}]
--------------------------------------------------
4. status
Counter({'resolvida': 20})
--------------------------------------------------
5. por_unidade
[('CGH PICADAS ALTAS', 6), ('CGH-APARECIDA', 4), ('CGH-PICADAS ALTAS', 4), ('CGH-FAE', 2), ('PCH-PEDRAS', 2), ('CGH HOPPEN', 1), ('PCG PEDRAS', 1)]
--------------------------------------------------
6. potencia_total_mw
0
--------------------------------------------------

Preciso identificar quais as diferenças de dados entre os dados mock e os dados reais existem, sem alterar o código existente, apenas identificar as diferenças.
Se puder imprimir as variaveis faltantes em cada variavel.



'''

'''
pagina: usinas.html

dados mock:

--------------------------------
usina
{'id': 1, 'nome': 'CGH-APARECIDA', 'sigla': 'APAR', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'status_operacional': 'operando', 'potencia_ativa_mw': 1200, 'mttr': '13h min', 'alarmes_por_hora': 8.0, 'alarmes_criticos': 0, 'incidentes_abertos': 1, 'alarmes_atencao': 3, 'alarmes_inundantes': 0, 'alarmes_oscilantes': 2, 'energia_nao_gerada_mwh': 0, 'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0}, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993), 'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)}
--------------------------------
usinas
[{'id': 1, 'nome': 'CGH-APARECIDA', 'sigla': 'APAR', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'status_operacional': 'operando', 'potencia_ativa_mw': 1200, 'mttr': '13h min', 'alarmes_por_hora': 8.0, 'alarmes_criticos': 0, 'incidentes_abertos': 1, 'alarmes_atencao': 3, 'alarmes_inundantes': 0, 'alarmes_oscilantes': 2, 'energia_nao_gerada_mwh': 0, 'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0}, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993), 'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)}, {'id': 2, 'nome': 'CGH-FAE', 'sigla': 'FAE', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'status_operacional': 'operando', 'potencia_ativa_mw': 950, 'mttr': '8h min', 'alarmes_por_hora': 5.2, 'alarmes_criticos': 0, 'incidentes_abertos': 0, 'alarmes_atencao': 1, 'alarmes_inundantes': 0, 'alarmes_oscilantes': 0, 'energia_nao_gerada_mwh': 0, 'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0}, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 354315), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 354315)}, {'id': 3, 'nome': 'CGH-HOPPEN', 'sigla': 'HOPP', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'status_operacional': 'operando', 'potencia_ativa_mw': 850, 'mttr': '20 min', 'alarmes_por_hora': 0.21, 'alarmes_criticos': 0, 'incidentes_abertos': 0, 'alarmes_atencao': 2, 'alarmes_inundantes': 0, 'alarmes_oscilantes': 1, 'energia_nao_gerada_mwh': 0, 'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0}, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 558514), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 558514)}, {'id': 4, 'nome': 'CGH-PICADAS ALTAS', 'sigla': 'PICALT', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'status_operacional': 'manutencao', 'potencia_ativa_mw': 0, 'mttr': 'N/A', 'alarmes_por_hora': 0, 'alarmes_criticos': 1, 'incidentes_abertos': 1, 'alarmes_atencao': 0, 'alarmes_inundantes': 0, 'alarmes_oscilantes': 0, 'energia_nao_gerada_mwh': 120, 'distribuicao_prioridade': {'alta': 100, 'media': 0, 'baixa': 0}, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 766481), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 766481)}, {'id': 5, 'nome': 'PCH-PEDRAS', 'sigla': 'PEDR', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'status_operacional': 'operando', 'potencia_ativa_mw': 1150, 'mttr': '10h min', 'alarmes_por_hora': 3.45, 'alarmes_criticos': 0, 'incidentes_abertos': 0, 'alarmes_atencao': 1, 'alarmes_inundantes': 0, 'alarmes_oscilantes': 0, 'energia_nao_gerada_mwh': 0, 'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0}, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 969718), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 969718)}]
--------------------------------
sigla
APAR
--------------------------------

dados reais:

--------------------------------
usina
{'id': 1, 'nome': 'CGH-APARECIDA', 'sigla': 'APAR', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993), 'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)}
--------------------------------
usinas
[{'id': 1, 'nome': 'CGH-APARECIDA', 'sigla': 'APAR', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993), 'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)}, {'id': 2, 'nome': 'CGH-FAE', 'sigla': 'FAE', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 354315), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 354315)}, {'id': 3, 'nome': 'CGH-HOPPEN', 'sigla': 'HOPP', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 558514), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 558514)}, {'id': 4, 'nome': 'CGH-PICADAS ALTAS', 'sigla': 'PICALT', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 766481), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 766481)}, {'id': 5, 'nome': 'PCH-PEDRAS', 'sigla': 'PEDR', 'timezone': 'America/Sao_Paulo', 'ativo': 1, 'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 969718), 'updated_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 969718)}]
--------------------------------
sigla
APAR
--------------------------------
'''
'''
1_initStatusUsinas
2_setup: É chamada pela 1_initStatusUsinas assim que a estrutura da página (DOM) está pronta. Sua tarefa é preparar o ambiente, o que inclui chamar a próxima função da sequência.
3_verificarSocket:Iniciada pela 2_setup, esta função fica em um loop, verificando a cada 400ms se a conexão com o Socket.IO (window.socket) já está disponível para uso.
4_solicitar: Assim que a 3_verificarSocket confirma que a conexão existe, esta função é chamada com o parâmetro 'inicial'. Ela serve como um invólucro (wrapper) para a próxima função.
5_solicitarStatus: Chamada pela 4_solicitar, esta é a função que efetivamente envia a mensagem solicitar_status_usinas para o servidor, pedindo os dados pela primeira vez.
6_handleStatusPayload: Esta função não é chamada diretamente na sequência, mas fica "escutando". Ela é executada automaticamente quando o servidor responde com o evento status_usinas_dados, trazendo os dados das usinas.
7_applyStatus: Após a 6_handleStatusPayload receber e validar os dados, ela chama esta função para cada usina. A 7_applyStatus localiza a área correta no HTML para exibir as informações.
8_renderBadge: É chamada pela 7_applyStatus para gerar o código HTML dos "badges" coloridos que mostram o status de cada dispositivo da usina.
9_getColorByDescription: Esta é uma função auxiliar, chamada pela 8_renderBadge. Sua única função é olhar a descrição do status (ex: "sincronizado") e retornar o conjunto de cores correto para o badge.
10_renderStatusDetalhes: Também chamada pela 7_applyStatus, mas só é útil se houver um local específico na página para mostrar uma lista mais detalhada dos status (o que não parece ser o caso no home.html atual, mas a função existe).

--------------------------------

1_initStatusUsinas (executa logo que o script de home.html carrega e registra setup para o DOM pronto)
2_setup (chamado no DOMContentLoaded, inicia a verificação do socket e do DOM)
3_verificarSocket (confere window.socket, registra listeners, cria o intervalo e chama solicitar quando o socket está pronto)
4_solicitar (função interna de verificarSocket que loga o tipo da solicitação e chama solicitarStatus)
5_solicitarStatus (aplica o controle de throttle e emite socket.emit('solicitar_status_usinas'))
6_handler_status_usinas_dados (listener registrado no socket, recebe o payload e chama handleStatusPayload)
7_handleStatusPayload (valida os dados, itera sobre as usinas e dispara applyStatus para cada uma)
8_applyStatus (seleciona elementos no DOM e usa renderBadge e renderStatusDetalhes para atualizar a UI)
9_renderBadge (gera o HTML das badges de dispositivos chamando getColorByDescription conforme necessário)
10_getColorByDescription (mapeia a descrição do status para classes de cor, devolvendo as opções corretas)
11_renderStatusDetalhes (monta a listagem textual dos dispositivos e seus status para o painel de detalhes)
'''
'''
Atualmente, tenho o seguinte payload que é enviado pelo socket.io:

{
    "success": true,
    "timestamp": 1763141130.0331209,
    "usinas": [
        {
            "nome": "CGH APARECIDA",
            "slug": "cghaparecida",
            "dispositivos": {
                "UG-01": {
                    "nome": "UG-01",
                    "valores": {
                        "Status U.M.D.(sincronizado)": false,
                        "Status sincronizado": false,
                        "Status U.P.S.(pronta para sincroniza\u00e7\u00e3o)": false,
                        "Status U.P.G.M. (pronta para giro mec\u00e2nico)": true,
                        "Status U.P. (parada)": false
                    },
                    "descricao": "Status U.P.G.M. (pronta para giro mec\u00e2nico)",
                    "tempo_leitura": 0.16894912719726562,
                    "erro": null
                }
            }
        },
        {
            "nome": "CGH FAE",
            "slug": "cghfae",
            "dispositivos": {
                "UG-01": {
                    "nome": "UG-01",
                    "valores": {},
                    "descricao": "Sem conex\u00e3o",
                    "tempo_leitura": 0.0,
                    "erro": "[ERRO] [CGH FAE - UG-01] Timeout ao conectar em 192.168.10.2:502"
                },
                "UG-02": {
                    "nome": "UG-02",
                    "valores": {},
                    "descricao": "Sem conex\u00e3o",
                    "tempo_leitura": 0.0,
                    "erro": "[ERRO] [CGH FAE - UG-02] Timeout ao conectar em 192.168.10.3:502"
                }
            }
        },
        {
            "nome": "CGH HOPPEN",
            "slug": "cghhoppen",
            "dispositivos": {
                "UG-01": {
                    "nome": "UG-01",
                    "valores": {},
                    "descricao": "Sem conex\u00e3o",
                    "tempo_leitura": 0.0,
                    "erro": "[ERRO] [CGH HOPPEN - UG-01] Timeout ao conectar em 192.168.10.2:502"
                },
                "UG-02": {
                    "nome": "UG-02",
                    "valores": {},
                    "descricao": "Sem conex\u00e3o",
                    "tempo_leitura": 0.0,
                    "erro": "[ERRO] [CGH HOPPEN - UG-02] Timeout ao conectar em 192.168.10.3:502"
                }
            }
        },
        {
            "nome": "CGH PICADAS ALTAS",
            "slug": "cghpicadasaltas",
            "dispositivos": {
                "UG-01": {
                    "nome": "UG-01",
                    "valores": {
                        "Status U.M.D.(sincronizado)": false,
                        "Status sincronizado": false,
                        "Status U.P.S.(pronta para sincroniza\u00e7\u00e3o)": false,
                        "Status U.P.G.M. (pronta para giro mec\u00e2nico)": false,
                        "Status U.P. (parada)": true
                    },
                    "descricao": "Status U.P. (parada)",
                    "tempo_leitura": 0.27051758766174316,
                    "erro": null
                },
                "UG-02": {
                    "nome": "UG-02",
                    "valores": {
                        "Status U.M.D.(sincronizado)": false,
                        "Status sincronizado": false,
                        "Status U.P.S.(pronta para sincroniza\u00e7\u00e3o)": false,
                        "Status U.P.G.M. (pronta para giro mec\u00e2nico)": false,
                        "Status U.P. (parada)": true
                    },
                    "descricao": "Status U.P. (parada)",
                    "tempo_leitura": 0.28988218307495117,
                    "erro": null
                }
            }
        },
        {
            "nome": "PCH PEDRAS",
            "slug": "pchpedras",
            "dispositivos": {
                "UG-01": {
                    "nome": "UG-01",
                    "valores": {
                        "Status U.M.D.(sincronizado)": false,
                        "Status sincronizado": true,
                        "Status U.P.S.(pronta para sincroniza\u00e7\u00e3o)": false,
                        "Status U.P.G.M. (pronta para giro mec\u00e2nico)": false,
                        "Status U.P. (parada)": false
                    },
                    "descricao": "Status sincronizado",
                    "tempo_leitura": 0.2903432846069336,
                    "erro": null
                },
                "UG-02": {
                    "nome": "UG-02",
                    "valores": {
                        "Status U.M.D.(sincronizado)": false,
                        "Status sincronizado": false,
                        "Status U.P.S.(pronta para sincroniza\u00e7\u00e3o)": false,
                        "Status U.P.G.M. (pronta para giro mec\u00e2nico)": false,
                        "Status U.P. (parada)": true
                    },
                    "descricao": "Status U.P. (parada)",
                    "tempo_leitura": 0.2751028537750244,
                    "erro": null
                }
            }
        }
    ]
}

Mas vou precisar adaptar o payload para receber as outras leituras que estão na imagem, sendo assim, preciso taxonar o payload para receber as outras leituras e pode escalar.
Pode me ajudar a taxonar o payload?
'''
'''
**FLUXO DE EXECUÇÃO - SALVAMENTO OP_PARADAS**

---

**1. TRIGGER INICIAL (Frontend)**
```
Usuario clica "Atualizar Status" 
  ↓
Frontend emite evento Socket.IO: "solicitar_status_usinas"
```

---

**2. HANDLER SOCKET.IO (status_usina.py)**
```
_1_register_status_usina_handler()
  ↓
_2_handle_status_usinas()
  - Incrementa contador de solicitações
  - Chama _3_build_status_payload()
```

---

**3. COLETA DE DADOS**
```
_3_build_status_payload()
  ↓
_4_coletar_status_usinas()
  - Carrega configurações do JSON
  - Cria event loop asyncio
  ↓
_6_coletar_status_async()
  - Cria tarefas paralelas para cada dispositivo (UG-01, UG-02...)
  - Executa todas simultaneamente
  ↓
_7_ler_status_dispositivo() [para cada UG]
  - Conecta via Modbus
  - Lê registradores de status e potência
  - Determina status geral
  - Retorna: {usina_nome, dispositivo_nome, status, potencia_ativa_mw, erro}
  ↓
Consolida resultados por usina
```

---

**4. MONTAGEM DO PAYLOAD**
```
Estrutura final:
{
  "success": true,
  "timestamp": 1763402183.95,
  "usinas": [
    {
      "nome": "CGH APARECIDA",
      "slug": "cghaparecida",
      "dispositivos": {
        "UG-01": {
          "nome": "UG-01",
          "potencia_ativa_mw": 392.0,
          "descricao": "Status sincronizado",
          "tempo_leitura": 0.19,
          "erro": null
        }
      }
    },
    ...
  ]
}
```

---

**5. SALVAMENTO NO BANCO**
```
_salvar_snapshot_json(payload)
  ↓
OpParadasCreate().insert({
  "dados": json.dumps(payload)  // serializa payload completo
})
  ↓
MySQL INSERT:
  INSERT INTO op_paradas (timestamp, dados) 
  VALUES (NOW(), '{"success":true,"timestamp":...}')
  ↓
1 linha criada com timestamp automático
```

---

**6. EMISSÃO PARA FRONTEND**
```
emit("status_usinas_dados", payload, broadcast=True)
  ↓
Todos os clientes conectados recebem o payload
  ↓
Frontend atualiza interface em tempo real
```

---

**RESULTADO FINAL NA TABELA**

```sql
op_paradas:
+----+----------------------------+------------------+
| id | timestamp                  | dados (JSON)     |
+----+----------------------------+------------------+
| 1  | 2025-11-17 17:54:57.123456 | {"success":true, |
|    |                            |  "timestamp":...,|
|    |                            |  "usinas":[...]} |
+----+----------------------------+------------------+
```

---

**FREQUÊNCIA**: 1 linha a cada solicitação (manual ou automática a cada 30s)

**VOLUME**: ~2.880 linhas/dia (se automático 30s) ou sob demanda (se manual)

'''
'''
Analise sem CDN:

## AI

### Analyzing trace

**Trace:**
````
URL: http://127.0.0.1:5001/
Bounds: {min: 75077200954, max: 75082410664}
CPU throttling: none
Network throttling: none
Metrics (lab / observed):
  - LCP: 136 ms, event: (eventKey: r-3797, ts: 75077341075), nodeId: 25
  - LCP breakdown:
    - TTFB: 4 ms, bounds: {min: 75077205009, max: 75077208889}
    - Render delay: 132 ms, bounds: {min: 75077208889, max: 75077341075}
  - CLS: 0.06, event: (eventKey: s--1, ts: 75077335626)
Metrics (field / real users): n/a – no data for this page in CrUX
Available insights:
  - insight name: LCPBreakdown
    description: Each [subpart has specific improvement strategies](https://web.dev/articles/optimize-lcp#lcp-breakdown). Ideally, most of the LCP time should be spent on loading the resources, not within delays.
    relevant trace bounds: {min: 75077205009, max: 75077341075}
    example question: Help me optimize my LCP score
    example question: Which LCP phase was most problematic?
    example question: What can I do to reduce the LCP time for this page load?
  - insight name: CLSCulprits
    description: Layout shifts occur when elements move absent any user interaction. [Investigate the causes of layout shifts](https://web.dev/articles/optimize-cls), such as elements being added, removed, or their fonts changing as the page loads.
    relevant trace bounds: {min: 75077335626, max: 75078610618}
    example question: Help me optimize my CLS score
    example question: How can I prevent layout shifts on this page?
  - insight name: RenderBlocking
    description: Requests are blocking the page's initial render, which may delay LCP. [Deferring or inlining](https://web.dev/learn/performance/understanding-the-critical-path#render-blocking_resources) can move these network requests out of the critical path.
    relevant trace bounds: {min: 75077217731, max: 75077271239}
    estimated metric savings: FCP 0 ms, LCP 0 ms
    example question: Show me the most impactful render blocking requests that I should focus on
    example question: How can I reduce the number of render blocking requests?
  - insight name: NetworkDependencyTree
    description: [Avoid chaining critical requests](https://developer.chrome.com/docs/lighthouse/performance/critical-request-chains) by reducing the length of chains, reducing the download size of resources, or deferring the download of unnecessary resources to improve page load.
    relevant trace bounds: {min: 75077205454, max: 75077406028}
    example question: How do I optimize my network dependency tree?
  - insight name: DocumentLatency
    description: Your first network request is the most important.  Reduce its latency by avoiding redirects, ensuring a fast server response, and enabling text compression.
    relevant trace bounds: {min: 75077205454, max: 75077220633}
    estimated metric savings: FCP 0 ms, LCP 0 ms
    estimated wasted bytes: 28.4 kB
    example question: How do I decrease the initial loading time of my page?
    example question: Did anything slow down the request for this document?
  - insight name: ThirdParties
    description: 3rd party code can significantly impact load performance. [Reduce and defer loading of 3rd party code](https://web.dev/articles/optimizing-content-efficiency-loading-third-party-javascript/) to prioritize your page's content.
    relevant trace bounds: {min: 75077217731, max: 75077412181}
    example question: Which third parties are having the largest impact on my page performance?
  - insight name: Cache
    description: A long cache lifetime can speed up repeat visits to your page. [Learn more](https://web.dev/uses-long-cache-ttl/).
    relevant trace bounds: {min: 75077217976, max: 75077227617}
    estimated metric savings: FCP 0 ms, LCP 0 ms
    example question: What caching strategies can I apply to improve my page performance?
````

### Investigating insight LCPBreakdown…

**Code executed:**
```
getInsightDetails('LCPBreakdown')
```

**Data returned:**
```
{"details":"## Insight Title: LCP breakdown\n\n## Insight Summary:\nThis insight is used to analyze the time spent that contributed to the final LCP time and identify which of the 4 phases (or 2 if there was no LCP resource) are contributing most to the delay in rendering the LCP element.\n\n## Detailed analysis:\nThe Largest Contentful Paint (LCP) time for this navigation was 136 ms.\nThe LCP element is text and was not fetched from the network.\n\nWe can break this time down into the 2 phases that combine to make the LCP time:\n\n- Time to first byte: 4 ms (2.9% of total LCP time)\n- Element render delay: 132 ms (97.1% of total LCP time)\n\n## Estimated savings: none\n\n## External resources:\n- https://web.dev/articles/lcp\n- https://web.dev/articles/optimize-lcp"}
```

### Answer

Com certeza, posso analisar o desempenho da sua página e apontar os tempos de carregamento e os módulos que contribuem para os piores tempos.

Seu [LCP (Largest Contentful Paint) foi de 136 ms](#r-3797). O elemento LCP é um elemento de texto [com nodeId 25](#node-25), que não foi buscado pela rede.

O detalhamento do LCP é o seguinte:
*   **Tempo para o primeiro byte (TTFB)**: 4 ms (2.9% do tempo total do LCP)
*   **Atraso na renderização do elemento**: 132 ms (97.1% do tempo total do LCP)

O "Atraso na renderização do elemento" é o tempo mais significativo aqui, indicando que a maior parte do tempo do LCP foi gasta na renderização do elemento LCP no navegador após a chegada dos dados.

Para entender quais módulos contribuem para os piores tempos, podemos focar nas atividades da thread principal com maior "self time" (tempo gasto diretamente na atividade, excluindo os filhos).

**Principais atividades da thread principal com maior impacto (piores tempos):**

*   **Compile script**: 48 ms. Este tempo é gasto compilando scripts JavaScript.
*   **Parse stylesheet**: 35 ms. Este tempo é gasto analisando folhas de estilo CSS.
*   **Layout**: 29 ms. Este tempo é gasto recalculando a geometria e a posição dos elementos na página.
*   **Recalculate style**: 24 ms. Este tempo é gasto recalculando os estilos dos elementos.

Além disso, existem contribuições de terceiros que impactam a thread principal:
*   **Google Tradutor**: 47 ms na thread principal.
*   **Leitura Rápida | Speed Reading**: 18 ms na thread principal.
*   **socket.io**: 7 ms na thread principal.

Com base nisso, as áreas mais impactantes para investigar e otimizar são:

1.  **Atraso na renderização do elemento LCP (132 ms)**: Precisamos entender o que está causando esse atraso na renderização do elemento de texto. Isso pode estar relacionado a script, estilos ou layout que precisam ser processados antes que o texto possa ser exibido.
2.  **Compilação de scripts e Análise de stylesheets**: Reduzir a quantidade de JavaScript e CSS que precisa ser compilada e analisada pode melhorar significativamente o tempo de renderização.

Gostaria de investigar mais a fundo o "Atraso na renderização do elemento" ou focar na otimização de scripts e stylesheets?

Com CDN:

## AI

### Analyzing trace

**Trace:**
````
URL: http://127.0.0.1:5001/
Bounds: {min: 75396991082, max: 75402131093}
CPU throttling: none
Network throttling: none
Metrics (lab / observed):
  - LCP: 59 ms, event: (eventKey: r-2812, ts: 75397054453), nodeId: 11
  - LCP breakdown:
    - TTFB: 3 ms, bounds: {min: 75396995415, max: 75396998730}
    - Render delay: 56 ms, bounds: {min: 75396998730, max: 75397054453}
  - CLS: 0.16, event: (eventKey: s--1, ts: 75397079776)
Metrics (field / real users): n/a – no data for this page in CrUX
Available insights:
  - insight name: LCPBreakdown
    description: Each [subpart has specific improvement strategies](https://web.dev/articles/optimize-lcp#lcp-breakdown). Ideally, most of the LCP time should be spent on loading the resources, not within delays.
    relevant trace bounds: {min: 75396995415, max: 75397054453}
    example question: Help me optimize my LCP score
    example question: Which LCP phase was most problematic?
    example question: What can I do to reduce the LCP time for this page load?
  - insight name: CLSCulprits
    description: Layout shifts occur when elements move absent any user interaction. [Investigate the causes of layout shifts](https://web.dev/articles/optimize-cls), such as elements being added, removed, or their fonts changing as the page loads.
    relevant trace bounds: {min: 75397079776, max: 75398138448}
    example question: Help me optimize my CLS score
    example question: How can I prevent layout shifts on this page?
  - insight name: RenderBlocking
    description: Requests are blocking the page's initial render, which may delay LCP. [Deferring or inlining](https://web.dev/learn/performance/understanding-the-critical-path#render-blocking_resources) can move these network requests out of the critical path.
    relevant trace bounds: {min: 75397002920, max: 75397014890}
    estimated metric savings: FCP 0 ms, LCP 0 ms
    example question: Show me the most impactful render blocking requests that I should focus on
    example question: How can I reduce the number of render blocking requests?
  - insight name: NetworkDependencyTree
    description: [Avoid chaining critical requests](https://developer.chrome.com/docs/lighthouse/performance/critical-request-chains) by reducing the length of chains, reducing the download size of resources, or deferring the download of unnecessary resources to improve page load.
    relevant trace bounds: {min: 75396995862, max: 75397134438}
    example question: How do I optimize my network dependency tree?
  - insight name: DocumentLatency
    description: Your first network request is the most important.  Reduce its latency by avoiding redirects, ensuring a fast server response, and enabling text compression.
    relevant trace bounds: {min: 75396995862, max: 75397006132}
    estimated metric savings: FCP 0 ms, LCP 0 ms
    estimated wasted bytes: 28.4 kB
    example question: How do I decrease the initial loading time of my page?
    example question: Did anything slow down the request for this document?
  - insight name: ThirdParties
    description: 3rd party code can significantly impact load performance. [Reduce and defer loading of 3rd party code](https://web.dev/articles/optimizing-content-efficiency-loading-third-party-javascript/) to prioritize your page's content.
    relevant trace bounds: {min: 75397002920, max: 75397133543}
    example question: Which third parties are having the largest impact on my page performance?
  - insight name: Cache
    description: A long cache lifetime can speed up repeat visits to your page. [Learn more](https://web.dev/uses-long-cache-ttl/).
    relevant trace bounds: {min: 75397003154, max: 75397015005}
    estimated metric savings: FCP 0 ms, LCP 0 ms
    example question: What caching strategies can I apply to improve my page performance?
````

### Answer

Com certeza! Vamos analisar a performance da sua página.

Baseado nas informações fornecidas, identifiquei alguns pontos onde a performance pode ser melhorada.

### Pontos de atenção para otimização

1.  **Layout Shift (CLS)**:
    *   Sua página apresenta um [CLS de 0.16](#s--1). Um CLS ideal deve ser inferior a 0.1.
    *   Este layout shift ocorre devido a uma atividade que durou 42 ms [aqui](#r-3443).
    *   Para entender as causas, precisamos investigar qual elemento está causando a mudança de layout e qual script ou estilo o está modificando. O maior impacto em "Self time" para layout é de 22 ms.
    *   **Impacto**: Afeta a experiência do usuário, tornando a página instável e potencialmente causando cliques errados.

2.  **LCP Render Delay**:
    *   O Largest Contentful Paint (LCP) da sua página é de 59 ms, o que é um bom valor.
    *   A maior parte desse tempo, 56 ms, é atribuída ao "Render Delay". Este delay é o tempo que leva desde que o recurso LCP é baixado até que seja renderizado na tela. O elemento LCP é uma imagem [aqui](#node-11).
    *   O insight [LCPBreakdown](#LCPBreakdown) sugere que idealmente, a maior parte do tempo do LCP deveria ser gasto no carregamento dos recursos, não em atrasos.
    *   **Impacto**: Embora o LCP esteja bom, reduzir esse atraso pode torná-lo ainda mais rápido.

3.  **Tarefas Longas na Thread Principal**:
    *   A thread principal teve uma tarefa que durou 42 ms [aqui](#r-3443), e outras duas de 27 ms [aqui](#r-1959) e 20 ms [aqui](#r-2770). Tarefas longas podem bloquear a renderização e a capacidade de resposta da página.
    *   A atividade de "Compile script" consome 47 ms de self time, e "Layout" consome 22 ms de self time, o que são atividades significativas na thread principal.
    *   **Impacto**: Pode causar lentidão na interação com a página e atrasar a renderização.

4.  **Recursos Render-Blocking**:
    *   Existem requisições que estão bloqueando a renderização inicial da página, o que pode atrasar o LCP, conforme indicado pelo insight [RenderBlocking](#RenderBlocking).
    *   Os recursos render-blocking identificados são:
        *   [`https://cdn.socket.io/4.7.2/socket.io.min.js`](#s-1027) (JavaScript, 10 ms de duração total)
        *   [`https://fonts.googleapis.com/icon?family=Material+Icons`](#s-1018) (CSS, 10 ms de duração total)
        *   [`https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap`](#s-1017) (CSS, 9 ms de duração total)
        *   [`https://cdn.tailwindcss.com/3.4.17?plugins=forms@0.5.10,typography@0.5.16,container-queries@0.1.1`](#s-1556) (JavaScript, 12 ms de duração total)
        *   [`http://127.0.0.1:5001/static/css/styles.css`](#s-1022) (CSS, 11 ms de duração total)
    *   **Impacto**: Atrasam o tempo em que o navegador pode começar a renderizar o conteúdo da página.

### Módulos e Componentes com Pior Tempo

Com base no resumo bottom-up e em atividades de terceiros, os módulos que mais contribuem para o tempo na thread principal são:

*   **Compilação de Script**: 47 ms de tempo próprio. Isso pode ser causado por grandes arquivos JavaScript sendo compilados.
*   **Layout**: 22 ms de tempo próprio. Mudanças no layout podem ser caras e indicar otimizações necessárias no CSS ou na estrutura do DOM.
*   **Google Tradutor**: 46 ms de tempo na thread principal. Scripts de terceiros como este podem impactar significativamente a performance.
*   **Leitura Rápida | Speed Reading**: 18 ms de tempo na thread principal. Outro script de extensão ou de terceiro que consome tempo da CPU.
*   **socket.io**: 6 ms de tempo na thread principal e 49.7 kB de transferência de rede. Embora não seja o maior tempo na thread principal, é um recurso render-blocking e seu uso contínuo pode impactar a interatividade.


'''