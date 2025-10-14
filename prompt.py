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
                        'socket.io.js','tests','.git','.cursor','test.py','amv','docs','testes','.py','analise_relatorios.html',
                        'registro_eventos.html','usinas.html']
        list_include = ['.html', '.css', '.js','.yaml']
        list_imprimir = ['.py','.html','.css','.js','.yaml']
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