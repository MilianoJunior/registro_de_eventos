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
                        'socket.io.js','tests','.git','.cursor','test.py','amv','docs','testes']
        list_include = ['.py', '.html', '.css', '.js','.yaml']
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
[
    {
    'id': 1, 
    'usina_id': 1, 
    'operador_id': 4, 
    'tipo': 'Evento', 
    'categoria': 'Operação/Humano', 
    'unidade': 
    'CGH-APARECIDA', 
    'tags': '', 
    'playbook': None, 
    'template_texto': None, 
    'descricao': 'Operação: Diminuição de potência 2400->2000\nCondição: Diferencial de grade 1.20 m\nResultado: Diferencial de grade abaixou para 1.00 m\nObservação: Leandro informou que o limpa grades está indisponível, sendo necessario baixar a potência progressivamente no valor de 200 kw.', 
    'status': 'resolvida', 
    'severidade': 'média', 
    'origem': 'humano', 
    'metadata': None, 
    'created_at': datetime.datetime(2025, 6, 23, 23, 0), 
    'updated_at': datetime.datetime(2025, 9, 12, 19, 55, 38), 
    'resolved_at': datetime.datetime(2025, 6, 23, 23, 0)
    }
]

[
    {
    'id': 1, 
    'nome': 'CGH-APARECIDA', 
    'sigla': 'APAR', 
    'timezone': 'America/Sao_Paulo', 
    'ativo': 1, 
    'created_at': datetime.datetime(2025, 9, 23, 14, 28, 29, 150993), 
    'updated_at': datetime.datetime(2025, 9, 23, 21, 21, 11, 659664)
    }, 
]

/* */

  /* */
'''