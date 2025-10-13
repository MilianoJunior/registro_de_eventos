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


<!DOCTYPE html>
<html class="dark" lang="pt-BR"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Dashboard de Ocorrências</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,typography,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"/>
<style type="text/tailwindcss">
    :root {
      --color-bg: #f8fafc;
      --color-bg-alt: #ffffff;
      --color-surface: #ffffff;
      --color-text: #0f172a;
      --color-text-muted: #64748b;
      --color-accent: #3b82f6;
      --color-accent-active: #2563eb;
      --color-accent-text: #ffffff;
      --color-success: #22C55E;
      --color-warning: #F59E0B;
      --color-danger: #EF4444;
      --sidebar-bg: #f8fafc;
    }
    .dark {
      --color-bg: #0f172a;
      --color-bg-alt: #1e293b;
      --color-surface: #1e293b;
      --color-text: #e2e8f0;
      --color-text-muted: #94a3b8;
      --color-accent: #3b82f6;
      --color-accent-active: #60a5fa;
      --color-accent-text: #ffffff;
      --color-success: #22c55e;
      --color-warning: #eab308;
      --color-danger: #ef4444;
      --sidebar-bg: #1e293b;
    }
    body {
      background-color: var(--color-bg);
      color: var(--color-text);
      font-family: 'Roboto', sans-serif;
    }
    .sidebar-item-active {
        background-color: var(--color-accent);
        color: var(--color-accent-text);
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3), 0 2px 4px -2px rgba(59, 130, 246, 0.2);
    }
    .sidebar-item-active .material-icons {
        color: var(--color-accent-text);
    }
     .sidebar-item:hover {
        background-color: rgba(100, 116, 139, 0.1);
    }
    .dark .sidebar-item:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    [x-cloak] { display: none !important; }
  </style>
<script>
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            primary: 'var(--color-accent)',
            background: 'var(--color-bg)',
            'background-alt': 'var(--color-bg-alt)',
            surface: 'var(--color-surface)',
            'text-primary': 'var(--color-text)',
            'text-muted': 'var(--color-text-muted)',
            success: 'var(--color-success)',
            warning: 'var(--color-warning)',
            danger: 'var(--color-danger)'
          },
          fontFamily: {
            display: ["Roboto", "sans-serif"],
          },
          borderRadius: {
            'DEFAULT': '0.5rem',
            'lg': '1rem',
            'xl': '1.5rem',
          },
        },
      },
    };
  </script>
<script defer="" src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="font-display">
<div class="flex h-screen bg-background">
<aside class="w-64 flex flex-col bg-[var(--sidebar-bg)] border-r border-slate-200 dark:border-slate-800 transition-all duration-300 ease-in-out">
<div class="flex items-center justify-center h-20 border-b border-slate-200 dark:border-slate-800 px-4">
<h1 class="text-xl font-bold text-text-primary flex items-center">
<span class="text-white">Enge<span class="text-blue-400">SEP</span></span>
<span class="font-light text-slate-400 ml-2">O&amp;M</span>
</h1>
</div>
<nav class="flex-1 space-y-2 p-4">
<a class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium sidebar-item-active" href="#">
<span class="material-icons text-base">dashboard</span>
<span class="ml-3">Visão Geral</span>
</a>
<a class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium text-text-muted hover:text-text-primary sidebar-item" href="#">
<span class="material-icons text-base">add_circle_outline</span>
<span class="ml-3">Registrar Evento</span>
</a>
<a class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium text-text-muted hover:text-text-primary sidebar-item" href="#">
<span class="material-icons text-base">analytics</span>
<span class="ml-3">Análise &amp; Relatórios</span>
</a>
<div class="pt-4 mt-4 border-t border-slate-200 dark:border-slate-800">
<h6 class="px-4 text-xs font-semibold text-text-muted uppercase tracking-wider">Usinas</h6>
<div class="mt-2 space-y-1">
<a class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium text-text-muted hover:text-text-primary sidebar-item" href="#">
<span class="material-icons text-base">factory</span>
<span class="ml-3">Usina Alpha</span>
</a>
<a class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium text-text-muted hover:text-text-primary sidebar-item" href="#">
<span class="material-icons text-base">factory</span>
<span class="ml-3">Usina Beta</span>
</a>
<a class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium text-text-muted hover:text-text-primary sidebar-item" href="#">
<span class="material-icons text-base">factory</span>
<span class="ml-3">Usina Gamma</span>
</a>
<a class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium text-text-muted hover:text-text-primary sidebar-item" href="#">
<span class="material-icons text-base">factory</span>
<span class="ml-3">Usina Delta</span>
</a>
</div>
</div>
</nav>
<div class="p-4 border-t border-slate-200 dark:border-slate-800">
<p class="text-center text-xs text-text-muted">© 2025 EngeSEP Systems</p>
</div>
</aside>
<div class="flex-1 overflow-y-auto">
<div class="p-4 sm:p-6 lg:p-8 space-y-6 lg:space-y-8">
<div class="flex flex-wrap justify-between items-center gap-4">
<h1 class="text-2xl sm:text-3xl font-bold text-text-primary">Dashboard de Ocorrências</h1>
<button class="p-2 rounded-full bg-surface text-text-primary hover:bg-background-alt shadow-md" id="theme-toggle">
<span class="material-icons block dark:hidden">dark_mode</span>
<span class="material-icons hidden dark:block">light_mode</span>
</button>
</div>
<header class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 lg:gap-6">
<div class="bg-surface p-4 lg:p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
<h3 class="text-sm font-medium text-text-muted">POTÊNCIA ATIVA</h3>
<p class="text-3xl lg:text-4xl font-bold mt-2 text-text-primary">2050 <span class="text-xl lg:text-2xl">MW</span></p>
</div>
<div class="bg-surface p-4 lg:p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
<h3 class="text-sm font-medium text-text-muted">INCIDENTES ABERTOS</h3>
<p class="text-3xl lg:text-4xl font-bold text-danger mt-2">1</p>
</div>
<div class="bg-surface p-4 lg:p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
<h3 class="text-sm font-medium text-text-muted">ALARMES CRÍTICOS</h3>
<p class="text-3xl lg:text-4xl font-bold text-danger mt-2">2</p>
</div>
<div class="bg-surface p-4 lg:p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800">
<h3 class="text-sm font-medium text-text-muted">ALARMES DE ATENÇÃO</h3>
<p class="text-3xl lg:text-4xl font-bold text-warning mt-2">3</p>
</div>
</header>
<main class="space-y-6 lg:space-y-8">
<div class="bg-danger/10 border border-danger/50 p-4 lg:p-6 rounded-lg shadow-lg flex flex-wrap items-center justify-between gap-4">
<div class="flex items-center space-x-4">
<span class="material-icons text-danger text-3xl lg:text-4xl">error</span>
<div>
<p class="font-bold text-base lg:text-lg text-text-primary">Temperatura elevada no gerador 2</p>
<p class="text-sm text-text-muted">Usina Alpha - Equipamento</p>
<p class="text-xs text-text-muted mt-1">26/09/2025, 16:32:15 por Sistema SCADA</p>
</div>
</div>
<button class="bg-danger hover:bg-danger/90 text-white font-bold py-2 px-4 rounded-lg transition duration-300 ease-in-out flex items-center text-sm lg:text-base">
<span class="material-icons mr-2">visibility</span> Analisar
                        </button>
</div>
<div class="grid grid-cols-1 xl:grid-cols-2 gap-6 lg:gap-8">
<section>
<h2 class="text-xl lg:text-2xl font-bold mb-4 text-text-primary">Status das Usinas</h2>
<div class="space-y-4">
<div class="bg-surface p-4 lg:p-6 rounded-lg border border-slate-200 dark:border-slate-800 shadow-sm">
<div class="flex flex-wrap justify-between items-center mb-4 gap-2">
<h3 class="text-base lg:text-lg font-bold text-text-primary">CGH APARECIDA</h3>
<span class="bg-success/20 text-success text-xs font-bold px-3 py-1 rounded-full flex items-center">
<span class="material-icons text-sm mr-1">power</span>Operando
                                        </span>
</div>
<div class="grid grid-cols-2 gap-4 text-sm">
<div>
<p class="text-text-muted">Potência Ativa:</p>
<p class="font-bold text-base lg:text-lg text-text-primary">1200 MW</p>
</div>
<div>
<p class="text-text-muted">MTTR:</p>
<p class="font-bold text-base lg:text-lg text-text-primary">13h min</p>
</div>
<div>
<p class="text-text-muted">Alarmes/hora:</p>
<p class="font-bold text-sm lg:text-base text-text-primary">8.00</p>
</div>
<div>
<p class="text-text-muted">Alarmes Críticos:</p>
<p class="font-bold text-sm lg:text-base text-success">0</p>
</div>
</div>
</div>
<div class="bg-surface p-4 lg:p-6 rounded-lg border border-slate-200 dark:border-slate-800 shadow-sm">
<div class="flex flex-wrap justify-between items-center mb-4 gap-2">
<h3 class="text-base lg:text-lg font-bold text-text-primary">CGH PICADAS ALTAS</h3>
<span class="bg-warning/20 text-warning text-xs font-bold px-3 py-1 rounded-full flex items-center">
<span class="material-icons text-sm mr-1">warning</span>Manutenção
                                        </span>
</div>
<div class="grid grid-cols-2 gap-4 text-sm">
<div>
<p class="text-text-muted">Potência Ativa:</p>
<p class="font-bold text-base lg:text-lg text-text-primary">0 MW</p>
</div>
<div>
<p class="text-text-muted">MTTR:</p>
<p class="font-bold text-base lg:text-lg text-text-primary">N/A</p>
</div>
<div>
<p class="text-text-muted">Alarmes/hora:</p>
<p class="font-bold text-sm lg:text-base text-text-primary">0</p>
</div>
<div>
<p class="text-text-muted">Alarmes Críticos:</p>
<p class="font-bold text-sm lg:text-base text-danger">1</p>
</div>
</div>
</div>
<div class="bg-surface p-4 lg:p-6 rounded-lg border border-slate-200 dark:border-slate-800 shadow-sm">
<div class="flex flex-wrap justify-between items-center mb-4 gap-2">
<h3 class="text-base lg:text-lg font-bold text-text-primary">CGH HOPPEN</h3>
<span class="bg-success/20 text-success text-xs font-bold px-3 py-1 rounded-full flex items-center">
<span class="material-icons text-sm mr-1">power</span>Operando
                                        </span>
</div>
<div class="grid grid-cols-2 gap-4 text-sm">
<div>
<p class="text-text-muted">Potência Ativa:</p>
<p class="font-bold text-base lg:text-lg text-text-primary">850 MW</p>
</div>
<div>
<p class="text-text-muted">MTTR:</p>
<p class="font-bold text-base lg:text-lg text-text-primary">3h min</p>
</div>
<div>
<p class="text-text-muted">Alarmes/hora:</p>
<p class="font-bold text-sm lg:text-base text-text-primary">0.21</p>
</div>
<div>
<p class="text-text-muted">Alarmes Críticos:</p>
<p class="font-bold text-sm lg:text-base text-success">0</p>
</div>
</div>
</div>
</div>
</section>
<section>
<div class="flex flex-wrap justify-between items-center mb-4 gap-4">
<h2 class="text-xl lg:text-2xl font-bold text-text-primary">Registro de Ocorrências</h2>
<button class="bg-primary hover:opacity-90 text-white font-bold py-2 px-4 rounded-lg transition duration-300 ease-in-out flex items-center text-sm lg:text-base">
<span class="material-icons mr-2">add</span>Nova Ocorrência
                                </button>
</div>
<div class="space-y-4">
<div class="bg-surface p-4 rounded-lg flex items-start space-x-4 hover:shadow-lg transition-shadow cursor-pointer border border-slate-200 dark:border-slate-800">
<div class="w-10 h-10 rounded-full bg-warning flex-shrink-0 flex items-center justify-center text-white font-bold text-sm">VG</div>
<div class="flex-1">
<div class="flex flex-wrap justify-between items-start gap-2">
<p class="font-bold text-sm lg:text-base text-text-primary flex-1">Perda de comunicação com remota do vertedouro</p>
<span class="text-xs font-medium text-warning px-2 py-1 bg-warning/20 rounded-full whitespace-nowrap">Atenção</span>
</div>
<p class="text-sm text-text-muted">Usina Gamma - Automação/Comms</p>
<p class="text-xs text-text-muted mt-1">26/09/2025, 15:17:57 por Sistema SCADA</p>
</div>
</div>
<div class="bg-surface p-4 rounded-lg flex items-start space-x-4 hover:shadow-lg transition-shadow cursor-pointer border border-slate-200 dark:border-slate-800">
<div class="w-10 h-10 rounded-full bg-danger flex-shrink-0 flex items-center justify-center text-white font-bold text-sm">VD</div>
<div class="flex-1">
<div class="flex flex-wrap justify-between items-start gap-2">
<p class="font-bold text-sm lg:text-base text-text-primary flex-1">Falta de tensão da Celesc</p>
<span class="text-xs font-medium text-danger px-2 py-1 bg-danger/20 rounded-full whitespace-nowrap">Crítico</span>
</div>
<p class="text-sm text-text-muted">Usina Delta - Rede Concessionária</p>
<p class="text-xs text-text-muted mt-1">26/09/2025, 12:45:03 por Sistema SCADA</p>
</div>
</div>
<div class="bg-surface p-4 rounded-lg flex items-start space-x-4 hover:shadow-lg transition-shadow cursor-pointer border border-slate-200 dark:border-slate-800">
<div class="w-10 h-10 rounded-full bg-warning flex-shrink-0 flex items-center justify-center text-white font-bold text-sm">UA</div>
<div class="flex-1">
<div class="flex flex-wrap justify-between items-start gap-2">
<p class="font-bold text-sm lg:text-base text-text-primary flex-1">Temperatura elevada no transformador principal</p>
<span class="text-xs font-medium text-warning px-2 py-1 bg-warning/20 rounded-full whitespace-nowrap">Atenção</span>
</div>
<p class="text-sm text-text-muted">Usina Alpha - Equipamentos</p>
<p class="text-xs text-text-muted mt-1">26/09/2025, 11:30:10 por Sistema SCADA</p>
</div>
</div>
<div class="bg-surface p-4 rounded-lg flex items-start space-x-4 hover:shadow-lg transition-shadow cursor-pointer border border-slate-200 dark:border-slate-800">
<div class="w-10 h-10 rounded-full bg-danger flex-shrink-0 flex items-center justify-center text-white font-bold text-sm">UB</div>
<div class="flex-1">
<div class="flex flex-wrap justify-between items-start gap-2">
<p class="font-bold text-sm lg:text-base text-text-primary flex-1">Início de manutenção programada - Gerador 1</p>
<span class="text-xs font-medium text-danger px-2 py-1 bg-danger/20 rounded-full whitespace-nowrap">Crítico</span>
</div>
<p class="text-sm text-text-muted">Usina Beta - Manutenção</p>
<p class="text-xs text-text-muted mt-1">26/09/2025, 08:00:00 por Operador</p>
</div>
</div>
<div class="bg-surface p-4 rounded-lg flex items-start space-x-4 hover:shadow-lg transition-shadow cursor-pointer border border-slate-200 dark:border-slate-800">
<div class="w-10 h-10 rounded-full bg-warning flex-shrink-0 flex items-center justify-center text-white font-bold text-sm">UG</div>
<div class="flex-1">
<div class="flex flex-wrap justify-between items-start gap-2">
<p class="font-bold text-sm lg:text-base text-text-primary flex-1">Falha no sensor de vibração</p>
<span class="text-xs font-medium text-warning px-2 py-1 bg-warning/20 rounded-full whitespace-nowrap">Atenção</span>
</div>
<p class="text-sm text-text-muted">Usina Gamma - Sensores</p>
<p class="text-xs text-text-muted mt-1">25/09/2025, 22:15:40 por Sistema SCADA</p>
</div>
</div>
</div>
</section>
</div>
</main>
</div>
</div>
</div>
<script>
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle.addEventListener('click', () => {
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });
    if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark')
    } else {
        document.documentElement.classList.remove('dark')
    }
  </script>

</body></html>'''