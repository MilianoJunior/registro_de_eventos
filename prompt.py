import os
import ast

cont = 0
total_linhas = 0
count = 0



def estrutura_pastas_arquivos(caminho, prefixo="", imprimir=False, lista_arquivos=None):
    """
    Função recursiva que imprime o nome das pastas e o código dos arquivos Python, HTML, CSS e JavaScript encontrados.
    :param caminho: Caminho do diretório a ser listado.
    :param prefixo: Prefixo para formatação da saída.
    """
    global cont, total_linhas, count

    for item in os.listdir(caminho):
        item_path = os.path.join(caminho, item)
        list_exclude = ['__pycache__', '.idea', 'README.md', 'requirements.txt', 'prompt.py','__init__.py',
                        'socket.io.js','tests','.git','.cursor','test.py','amv','docs','testes','analise_relatorios.html','analiseController.py','.css']
        list_include = ['.html', '.js','.yaml','.py','.json']
        list_imprimir = ['.py','.html','.js','.yaml','.json']
        if item in list_exclude:
            continue

        if os.path.isdir(item_path):
            # Se o item é uma pasta, imprime o nome da pasta e faz a chamada recursiva
            cont += 1
            if not imprimir:
                print(f"{prefixo}{item}/")
            estrutura_pastas_arquivos(item_path, prefixo + "    ├── ", imprimir, lista_arquivos)
        elif os.path.isfile(item_path) and any([item.endswith(ext) for ext in list_include]):
            # Se o item é um arquivo Python, HTML, CSS ou JavaScript, imprime o nome do arquivo
            cont += 1
            if not imprimir:
                print(f"{prefixo}{item}")
                # print(f"{prefixo}├── {item}")

            if lista_arquivos is not None:
                if item in lista_arquivos:
                    print(f"{prefixo}{item}")
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
                continue


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
# estrutura_pastas_arquivos(path, "", imprimir=True)
print('-' * 50)
lista = ['rats_crud.py','ratsController.py','rats.html']
estrutura_pastas_arquivos(path, "", imprimir=True, lista_arquivos=lista)
# print('-' * 50)
# print('Métodos e funções dos arquivos Python:')

'''
Tenho o código abaixo que cria a imagem em anexo, mas preciso melhorar a visibilidade das temperaturas 

'''

'''
Testes criar rateio

  Campo cliente e obra
  1. Verificar se busca os clientes e preenche os outros campos automaticamente. OK

  Resumo do chamado
  1. Nada para verificar . OK

  Horas de serviço
  1. Verificar adicionar horas - OK
  2. Adicionar o campo km rodados ou remoto, tenho que mudar o banco de dados - OK

  Materiais utilizados
  1. Verificar adicionar materiais - OK
  2. Verificar se busca os materiais e preenche os outros campos automaticamente - OK

  Relatório Técnico
  1. Adicionar a IA para preenher automaticamente o relatório técnico, no campo descrição e conclusão - ok

  Fotos e assinaturas
  1. Verificar se busca as fotos e preenche e aparece a legenda - ok

  Salvar
  1. Verificar se salva - ok

Teste de Editar Rat

  Horas de serviço
  1. Verificar adicionar horas - ok
  2. Alterar o campo km rodados ou remoto, tenho que mudar o banco de dados - ok

  Materiais utilizados
  1. Verificar adicionar materiais - ok
  2. Verificar se busca os materiais e preenche os outros campos automaticamente - ok

  Relatório Técnico
  1. Adicionar a IA para preenher automaticamente o relatório técnico, no campo descrição e conclusão - ok

  Fotos e assinaturas
  1. Verificar se busca as fotos e preenche e aparece a legenda - ok

  Salvar
  1. Verificar se salva - ok

Implementar o mecanismo de busca na tabela de RATs
Corrigir o redirecionamento quando é salvo um novo rat para a página inicial do rat - ok
quando salvo um novo rat, recebo um alert de sucesso, temos que usar um alert personalizado - ok
'''
'''
Carga de clientes (frontend)
  Quantos operadores simultâneos no pior caso? (10? 50? 200?)
      É um COG(Central de Operação de Geração), se conecta via VPN Privada com Pequenas e Medias Usinas. O computador da usina tem uma API que
      se comunica com todos os dispositivos com Modbus TCP, as usinas tem no mínimo 3 dispositivos, no máximo 15 dispositivos, o tempo de resposta periódico pode ser de até 30 segundos.
      No máximo 5 clientes simultâneos, mas na maioria das vezes são 1 ou 2 clientes.
  Eles ficam mais em Home ou em página de usina?
      Eles ficam mais em Home, pois é a página principal e é onde é exibido o status das usinas.
  Quantas abas por operador (média/pior caso)?
      No máximo 3 abas por operador, mas na maioria das vezes são 1 ou 2 abas.

Carga de usinas/CLPs
  Quantas usinas no sistema hoje e em 6–12 meses?
     Atualmente estamos com 6 usinas, em 6–12 meses vamos ter 10 usinas.
  Quantas UGs por usina (média/pior)?
    No mínimo 1 UGs por usina, no máximo 4 UGs por usina.
  Leituras são via Modbus TCP direto ou via API/bridge (seu httpx sugere bridge)? Qual limite de conexões dessa bridge?
    Via API, criei uma API em python usando o Modbus TCP para ler as leituras de cada UG, essa API está rodando em computadores com Windows 11 pro como um serviço criado pelo pyinstaller e winsw.

Banco e auditoria
  Qual é o banco de dados usado?
    MySQL, todas as tabelas estão no arquivo libs/models/docs/cog_schema.py
  Qual é a estrutura de tabelas?
    Criei as tabelas necessárias para o sistema, como op_usinas, op_dispositivos, op_leituras, op_ocorrencias, op_ocorrencias_hist, op_ocorrencias_hist_detalhes, op_ocorrencias_hist_detalhes_hist, op_ocorrencias_hist_detalhes_hist_detalhes, op_ocorrencias_hist_detalhes_hist_detalhes_hist, op_ocorrencias_hist_detalhes_hist_detalhes_hist_detalhes.
  Auditoria
    A cada 30 segundos é realizado a persistência dos dados na tabela op_paradas, além disso, o operador vai inserir ocorrências na tabela op_ocorrencias.
    Depois de pronto, vou melhorar essa parte, mas temos que ter algo operacional que não seja só o dashaboard que os clientes acessam, temos um banco de dados
    com 30 colunas em média para cada unidade geradora, com valores de temperatura, pressão, vazão, vibração, etc.Esses dados são salvos no servidor da https://railway.com/
    e existe uma copia local que é sincronizada a cada 1 minuto com o servidor.

Estrutura 
   Gcloud
   Tenho uma VM configurada com o ubuntu-2204-jammy-v20251002, com e2-small (2 vCPUs, 2 GB de memória).
   Esse código vai ser executado nessa VM, vou mudar o mysql para o gcloud, esse delay de comunicação vai diminuir muito.
   A VM já está configurada com uma máquina da rede VPN Tailscale, então as configurações de conexão com a usina e a API já estão configuradas corretamente no arquivo config/usinas_dispositivos.json

OBS: Sou só eu que estou fazendo o COG, eu que modelei e fiz o meu irmão acreditar na ideia, pq ele trabalha com comissionamento de usinas na parte de montar paineis e
colocar as usinas em sincronia com a rede elétrica.
Tem mais alguns detalhes, mas é isso ai, acredito que talvez deveria existir um investimento em uma equipe ou então comprar um software tipo o grafana, elipse ou outro software de monitoramento, mas dai existiria a necessidade de investimentos em infraestrutura e manutenção de software que talvez não trouxessem um salto possível de 
oportunidade de negócio, sou policial penal e esse é meu segundo emprego, mas amo programar, pode até parecer bobo, mas me sinto muito bem quando estou aqui atras dessa mesa programando.




'''

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
'''
# # -------------------------------------------------------------------
# # FLUXO DO MÓDULO
# # 1. _periodo_para_intervalo -> define a janela de consulta por período
# # 2. Read -> repositório genérico para leituras SQL
# # 3. OpParadas.get_mttr_diario_all -> retorna eventos para cálculo de MTTR
# # -------------------------------------------------------------------

# from __future__ import annotations
# from typing import Any, Dict, List, Optional, Sequence, Union, Tuple
# from libs.models.database import Database
# from libs.models.utils.utils import safe_ident, columns_sql, build_where_clause, order_sql, limit_sql
# from datetime import datetime, timedelta
# import json

# PERIODOS_PARADAS = {'diario': 1, 'semanal': 7, 'mensal': 30, 'anual': 365}

# def _periodo_para_intervalo(periodo: str = 'diario') -> datetime:
#     dias = PERIODOS_PARADAS.get(periodo.lower(), 1)
#     return datetime.now() - timedelta(days=dias)

# Identifier = str
# Columns = Union[str, Sequence[Identifier]]

# class BaseReader:
#     tabela: str
#     colunas_padrao: Columns = "*"
#     order_padrao: str = "id"
#     desc_padrao: bool = False

#     def __init__(self, db: Optional[Database] = None):
#         self.db = db or Database()

#     def _select(
#         self,
#         where: Optional[Dict[str, Any]] = None,
#         colunas: Optional[Columns] = None,           # <-- pode sobrescrever as padrão
#         order_by: Optional[str] = None,
#         desc: Optional[bool] = None,
#         limit: Optional[int] = None,
#         offset: Optional[int] = None,
#         extra_clause: str = "",
#         extra_params: Tuple[Any, ...] = (),
#     ) -> List[Dict[str, Any]]:
#         self.db.connect()
        
#         # AQUI É O SEGREDO: se passar colunas explicitamente, usa elas. Senão, usa as padrão.
#         cols = columns_sql(colunas if colunas is not None else self.colunas_padrao)
#         sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"

#         params: List[Any] = []
#         if where:
#             clause, where_params = build_where_clause(where)
#             sql += clause
#             params.extend(where_params)

#         sql += extra_clause

#         sql += order_sql(
#             order_by or self.order_padrao,
#             desc if desc is not None else self.desc_padrao
#         )
#         sql += limit_sql(limit, offset)

#         final_params = tuple(params) + extra_params
#         return self.db.fetch_data(sql, final_params if final_params else None)

#     # Métodos de conveniência (continuam iguais)
#     def all(self, limit: Optional[int] = None, offset: Optional[int] = None):
#         return self._select(limit=limit, offset=offset)

#     def where(self, where: Dict[str, Any], limit: Optional[int] = None):
#         return self._select(where=where, limit=limit)

#     def one(self, where: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#         rows = self._select(where=where, limit=1)
#         return rows[0] if rows else None

#     def count(self, where: Optional[Dict[str, Any]]= None) -> int:
#         clause = ""
#         params = []
#         if where:
#             clause, params = build_where_clause(where)
#         sql = f"SELECT COUNT(*) AS total FROM {safe_ident(self.tabela)}{clause}"
#         row = self.db.fetch_data(sql, tuple(params))
#         return int(row[0]["total"]) if row else 0
# # from __future__ import annotations
# # from typing import Any, Dict, List, Optional, Sequence, Union
# # from libs.models.database import Database
# # from libs.models.utils.utils import safe_ident, columns_sql, build_where_clause, order_sql, limit_sql
# # from datetime import datetime, timedelta
# # import json


# # PERIODOS_PARADAS = {'diario': 1, 'semanal': 7, 'mensal': 30, 'anual': 365}
# # Identifier = str
# # Columns = Union[str, Sequence[Identifier]]

# # def _periodo_para_intervalo(periodo: str) -> datetime:
# #     dias = PERIODOS_PARADAS.get(periodo, PERIODOS_PARADAS['diario'])
# #     return datetime.now() - timedelta(days=dias)

# # class BaseReader:
# #     """
# #     BASE MÍNIMA E ETERNA.
# #     Só tem o que 99% das queries usam: where + order + limit + colunas flexíveis.
# #     Nada mais. Nunca mais vai inchar.
# #     """
# #     tabela: str
# #     colunas_padrao: Columns = "*"
# #     order_padrao: str = "id"
# #     desc_padrao: bool = False

# #     def __init__(self, db: Optional[Database] = None):
# #         self.db = db or Database()

# #     def _select(
# #         self,
# #         where: Optional[Dict[str, Any]] = None,
# #         colunas: Optional[Columns] = None,
# #         order_by: Optional[str] = None,
# #         desc: Optional[bool] = None,
# #         limit: Optional[int] = None,
# #         offset: Optional[int] = None,
# #         extra_clause: str = "",          # pra GROUP BY, HAVING, etc.
# #         params_extra: tuple = (),
# #     ) -> List[Dict[str, Any]]:
# #         self.db.connect()
# #         cols = columns_sql(colunas if colunas is not None else self.colunas_padrao)
# #         sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"

# #         params: List[Any] = []
# #         if where:
# #             clause, where_params = build_where_clause(where)
# #             sql += clause
# #             params.extend(where_params)

# #         sql += extra_clause
# #         sql += order_sql(order_by or self.order_padrao, desc if desc is not None else self.desc_padrao)
# #         sql += limit_sql(limit, offset)

# #         return self.db.fetch_data(sql, tuple(params + list(params_extra)))

# #     def all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
# #         return self._select(limit=limit, offset=offset)

# #     def where(self, where: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
# #         return self._select(where=where, limit=limit)

# #     def one(self, where: Dict[str, Any]) -> Optional[Dict[str, Any]]:
# #         rows = self._select(where=where, limit=1)
# #         return rows[0] if rows else None

# #     def count(self, where: Optional[Dict[str, Any]] = None) -> int:
# #         clause = ""
# #         params: List[Any] = []
# #         if where:
# #             clause, params = build_where_clause(where)
# #         sql = f"SELECT COUNT(*) AS total FROM {safe_ident(self.tabela)}{clause}"
# #         row = self.db.fetch_data(sql, tuple(params))
# #         return int(row[0]["total"]) if row else 0

# class OpUsina(BaseReader):
#     tabela = "op_usina"
#     colunas_padrao = ["id", "nome", "sigla", "ativo", "created_at"]
#     order_padrao = "nome"

# class OpUsuario(BaseReader):
#     tabela = "op_usuario"
#     colunas_padrao = ["id", "nome", "email", "perfil", "ativo"]
#     order_padrao = "nome"

# class OpOcorrencia(BaseReader):
#     tabela = "op_ocorrencia"
#     colunas_padrao = [
#         "id","usina_id","operador_id","tipo","categoria","unidade","tags",
#         "playbook","template_texto","descricao","status","severidade","origem",
#         "metadata","created_at","updated_at","resolved_at","requer_acao",
#         "data_ocorrencia","resolvida_por","resolucao_descricao"
#     ]
#     order_padrao = "created_at"
#     desc_padrao = True

#     def get_counts_by_status(self) -> Dict[str, int]:
#         rows = self._select(
#             colunas=["status", "COUNT(*) AS total"],           # só o que precisa
#             extra_clause="GROUP BY status"
#         )
#         return {r["status"]: r["total"] for r in rows} if rows else {}

#     def get_open_actions(self, limit: int = 20) -> List[Dict]:
#         return self.where({"requer_acao": 1, "resolvida_por": ("IS NULL", None)}, limit=limit)
#         # build_where_clause já suporta IS NULL quando valor é (operador, None)

# class OpParadas(BaseReader):
#     tabela = "op_paradas"
#     colunas_padrao = ["id", "timestamp", "dados"]
#     order_padrao = "timestamp"
#     desc_padrao = True

#     def get_indicadores_manutencao(self, periodo: str = 'diario') -> Dict[str, Any]:
#         """
#         Calcula MTTR e tempo de indisponibilidade baseado no histórico de snapshots.
#         Retorna: { 'slug_usina': { 'mttr_str': '2h 15m', 'mttr_minutos': 135, ... } }
#         """
#         try:
#             janela = _periodo_para_intervalo(periodo)
#             self.db.connect()
#             # Ordenado ASC para calcular a linha do tempo corretamente
#             rows = self._select(
#                     where={"timestamp": ("gte", janela)},
#                     order_by="timestamp",
#                     desc=False,  # precisa ASC pra cálculo de delta
#                     colunas=["timestamp", "dados"]
#                 )
            
#             if not rows:
#                 return {}

#             # Estruturas acumuladoras
#             # stats[slug_usina][nome_dispositivo] = { 'tempo_manutencao': 0, 'contagem': 0, 'em_manutencao': False }
#             stats = {}

#             for i in range(len(rows) - 1):
#                 atual = rows[i]
#                 proximo = rows[i+1]
                
#                 # Delta T em minutos
#                 dt_seconds = (proximo['timestamp'] - atual['timestamp']).total_seconds()
#                 dt_minutes = dt_seconds / 60.0
                
#                 # Evitar deltas gigantes (se o coletor ficou desligado 1 dia, não conta como manutenção)
#                 if dt_minutes > 60: 
#                     continue

#                 dados = atual['dados']
#                 if isinstance(dados, str):
#                     try:
#                         dados = json.loads(dados)
#                     except:
#                         continue
                
#                 # Estrutura do JSON: { 'usinas': [ { 'slug': '...', 'dispositivos': { ... } } ] }
#                 lista_usinas = dados.get('usinas', [])
                
#                 for usina in lista_usinas:
#                     slug = usina.get('slug')
#                     if not slug: continue
                    
#                     if slug not in stats: stats[slug] = {}
                    
#                     dispositivos = usina.get('dispositivos', {})
#                     for nome_disp, info in dispositivos.items():
#                         if nome_disp not in stats[slug]:
#                             stats[slug][nome_disp] = {'tempo_manutencao': 0.0, 'eventos': 0, 'ultimo_status_era_manutencao': False}
                        
#                         # Verifica status
#                         descricao = (info.get('descricao') or "").lower()
#                         em_manutencao = "manutenção" in descricao
                        
#                         # Contabiliza tempo
#                         if em_manutencao:
#                             stats[slug][nome_disp]['tempo_manutencao'] += dt_minutes
                            
#                         # Contabiliza eventos (borda de subida)
#                         if em_manutencao and not stats[slug][nome_disp]['ultimo_status_era_manutencao']:
#                             stats[slug][nome_disp]['eventos'] += 1
                            
#                         stats[slug][nome_disp]['ultimo_status_era_manutencao'] = em_manutencao

#             # Consolidar resultados por Usina
#             resultados = {}
#             for slug, disps in stats.items():
#                 tempo_total_usina = 0.0
#                 eventos_total_usina = 0
                
#                 for d in disps.values():
#                     tempo_total_usina += d['tempo_manutencao']
#                     eventos_total_usina += d['eventos']
                
#                 # MTTR da Usina (Média simples ou soma? Normalmente soma do tempo / soma dos eventos)
#                 mttr_minutos = 0
#                 if eventos_total_usina > 0:
#                     mttr_minutos = tempo_total_usina / eventos_total_usina
#                 elif tempo_total_usina > 0:
#                     # Se tem tempo mas não pegou o inicio do evento (evento veio de antes), considera 1 evento
#                     mttr_minutos = tempo_total_usina
                
#                 # Formatação amigável
#                 horas = int(mttr_minutos // 60)
#                 minutos = int(mttr_minutos % 60)
#                 mttr_str = f"{horas}h {minutos}m" if horas > 0 else f"{minutos} min"
                
#                 resultados[slug] = {
#                     'mttr_str': mttr_str if mttr_minutos > 0 else "0 min",
#                     'mttr_minutos': mttr_minutos,
#                     'eventos': eventos_total_usina
#                 }
                
#             return resultados

#         except Exception as e:
#             raise Exception(f"Erro: class: OpParadas, function: indicadores_manutencao: msg: {e}")
#             return {}

# # libs/models/read.py
# from __future__ import annotations

# # CONFIGURAÇÕES / CONSTANTES / MAPAS

# from datetime import datetime, timedelta
# from typing import Optional, Sequence, Union, Any, Dict, List, Tuple
# import json
# from libs.models.database import Database
# from libs.models.utils.utils import (
#     safe_ident, columns_sql, build_where_clause,
#     order_sql, limit_sql,
# )




# Identifier = str
# Columns = Union[str, Sequence[Identifier]]

# class Read:
#     """
#     Repositório de leitura simples (parametrizado, reutilizável).
#     """
#     def __init__(
#         self,
#         tabela: Identifier,
#         colunas: Optional[Columns] = None,
#         default_order_by: Optional[Identifier] = "id",
#         default_desc: bool = False,
#         db_instance: Optional[Database] = None,
#     ):
#         self.tabela = tabela
#         self.colunas = colunas if colunas is not None else "*"
#         self.default_order_by = default_order_by
#         self.default_desc = default_desc
#         self.db = db_instance or Database()

#     # ----------------- leituras básicas -----------------
#     def get_all(
#         self,
#         limit: Optional[int] = None,
#         offset: Optional[int] = None,
#         order_by: Optional[Identifier] = None,
#         desc: Optional[bool] = None,
#     ) -> List[Dict[str, Any]]:
#         try:
#             import time
#             self.db.connect()
#             cols = columns_sql(self.colunas)
#             sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"
#             sql += order_sql(order_by or self.default_order_by, self.default_desc if desc is None else bool(desc))
#             sql += limit_sql(limit, offset)
#             dados = self.db.fetch_data(sql)
#             return dados
#         except Exception as e:
#             self._error('Read', 'get_all', e)

#     def get_by_id(self, id_: int) -> Optional[Dict[str, Any]]:
#         try:
#             self.db.connect()
#             cols = columns_sql(self.colunas)
#             sql = f"SELECT {cols} FROM {safe_ident(self.tabela)} WHERE `id` = %s LIMIT 1"
#             rows = self.db.fetch_data(sql, (id_,))
#             return rows[0] if rows else None
#         except Exception as e:
#             self._error('Read', 'get_by_id', e)

#     def first(
#         self,
#         where: Optional[Dict[str, Any]] = None,
#         order_by: Optional[Identifier] = None,
#         desc: Optional[bool] = None,
#     ) -> Optional[Dict[str, Any]]:
#         rows = self.where(where or {}, limit=1, order_by=order_by, desc=desc)
#         return rows[0] if rows else None

#     def count(self, where: Optional[Dict[str, Any]] = None) -> int:
#         try:
#             self.db.connect()
#             sql = f"SELECT COUNT(*) AS total FROM {safe_ident(self.tabela)}"
#             params: List[Any] = []
#             if where:
#                 clause_params = build_where_clause(where)
#                 clause, params = clause_params if clause_params else ("", [])
#                 sql += clause
#             rows = self.db.fetch_data(sql, tuple(params))
#             return int(rows[0]["total"]) if rows else 0
#         except Exception as e:
#             self._error('Read', 'count', e)

#     # ----------------- filtros/where -----------------
#     def where(
#         self,
#         where: Dict[str, Any],
#         limit: Optional[int] = None,
#         offset: Optional[int] = None,
#         order_by: Optional[Identifier] = None,
#         desc: Optional[bool] = None,
#         columns: Optional[Columns] = None,
#     ) -> List[Dict[str, Any]]:
#         """
#         Operadores suportados (ver utils.build_where_clause):
#           =, IN, LIKE, LIKE_NORM, EQ_NORM, STARTSWITH_NORM, ENDSWITH_NORM,
#           NE, GT, GTE, LT, LTE, REGEXP
#         """
#         try:
#             self.db.connect()
#             cols = columns_sql(columns if columns is not None else self.colunas)
#             sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"
#             clause_params = build_where_clause(where)
#             clause, params = clause_params if clause_params else ("", [])
#             sql += clause
#             sql += order_sql(order_by or self.default_order_by, self.default_desc if desc is None else bool(desc))
#             sql += limit_sql(limit, offset)
#             return self.db.fetch_data(sql, tuple(params))
#         except Exception as e:
#             self._error('Read', 'where', e)

#     # ----------------- intervalos de data -----------------
#     def get_between(
#         self,
#         column: Identifier = "created_at",
#         start: Optional[datetime] = None,
#         end: Optional[datetime] = None,
#         limit: Optional[int] = None,
#         offset: Optional[int] = None,
#         order_by: Optional[Identifier] = None,
#         desc: Optional[bool] = None,
#     ) -> List[Dict[str, Any]]:
#         try:
#             self.db.connect()
#             col = safe_ident(column)
#             cols = columns_sql(self.colunas)

#             conds: List[str] = []
#             params: List[Any] = []

#             if start is not None:
#                 conds.append(f"{col} >= %s")
#                 params.append(start)
#             if end is not None:
#                 conds.append(f"{col} <= %s")
#                 params.append(end)

#             sql = f"SELECT {cols} FROM {safe_ident(self.tabela)}"
#             if conds:
#                 sql += " WHERE " + " AND ".join(conds)

#             sql += order_sql(order_by or self.default_order_by, self.default_desc if desc is None else bool(desc))
#             sql += limit_sql(limit, offset)
#             return self.db.fetch_data(sql, tuple(params))
#         except Exception as e:
#             self._error('Read', 'get_between', e)

#     # ----------------- utilidades -----------------
#     def ids_only(self, where: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[int]:
#         try:
#             self.db.connect()
#             sql = f"SELECT `id` FROM {safe_ident(self.tabela)}"
#             params: List[Any] = []
#             if where:
#                 clause_params = build_where_clause(where)
#                 clause, params = clause_params if clause_params else ("", [])
#                 sql += clause
#             sql += limit_sql(limit, 0)
#             rows = self.db.fetch_data(sql, tuple(params))
#             return [int(r["id"]) for r in rows]
#         except Exception as e:
#             self._error('Read', 'ids_only', e)

#     def _error(self, name, function, e):
#         raise Exception(f"Erro: class: {name}, function: {function}: msg: {e}")

# # ----------------- Models "fininhos" (op_) -----------------
# class OpUsina(BaseReader):
#     def __init__(self, colunas: Optional[Columns] = None, db_instance: Optional[Database] = None):
#         super().__init__(
#             "op_usina",
#             colunas or ["id", "nome", "sigla", "ativo", "created_at"],
#             default_order_by="nome",
#             db_instance=db_instance,
#         )

# class OpUsuario(BaseReader):
#     def __init__(self, colunas: Optional[Columns] = None, db_instance: Optional[Database] = None):
#         super().__init__(
#             "op_usuario",
#             colunas or ["id", "nome", "email", "perfil", "ativo"],
#             default_order_by="nome",
#             db_instance=db_instance,
#         )

# class OpOcorrencia(BaseReader):
#     def __init__(self, colunas: Optional[Columns] = None, db_instance: Optional[Database] = None):
#         super().__init__(
#             "op_ocorrencia",
#             colunas or [
#                 "id","usina_id","operador_id","tipo","categoria","unidade","tags",
#                 "playbook","template_texto","descricao",
#                 "status","severidade","origem","metadata",
#                 "created_at","updated_at","resolved_at",
#                 "requer_acao","data_ocorrencia","resolvida_por","resolucao_descricao"
#             ],
#             default_order_by="created_at",
#             default_desc=True,
#             db_instance=db_instance,
#         )

#     def get_counts_by_status(self) -> Dict[str, int]:
#         """Retorna contagem agrupada por status"""
#         sql = "SELECT status, COUNT(*) as total FROM op_ocorrencia GROUP BY status"
#         res = self.db.fetch_data(sql)
#         if not res:
#             return {}
#         return {r['status']: r['total'] for r in res}

#     def get_open_actions(self, limit=20) -> List[Dict]:
#         """Busca ocorrências que requerem ação e não estão resolvidas por completo"""
#         # Regra: requer_acao=1 E (resolvida_por IS NULL OR resolvida_por = '')
#         # Ajuste conforme a regra exata do usuário
#         return self.get_all(
#             conditions={
#                 "requer_acao": 1,
#                 # Opcional: adicionar filtro de resolvida_por se o método get_all suportar IS NULL ou custom query
#             },
#             limit=limit
#         )


# class OpParadas(BaseReader):
#     def __init__(self, colunas: Optional[Columns] = None, db_instance: Optional[Database] = None):
#         super().__init__(
#             "op_paradas",
#             colunas or ["id", "timestamp", "dados"],
#             default_order_by="timestamp",
#             default_desc=True,
#             db_instance=db_instance,
#         )
#     def get_indicadores_manutencao(self, periodo: str = 'diario') -> Dict[str, Any]:
#         """
#         Calcula MTTR e tempo de indisponibilidade baseado no histórico de snapshots.
#         Retorna: { 'slug_usina': { 'mttr_str': '2h 15m', 'mttr_minutos': 135, ... } }
#         """
#         try:
#             janela = _periodo_para_intervalo(periodo)
#             self.db.connect()
#             # Ordenado ASC para calcular a linha do tempo corretamente
#             sql = f"SELECT timestamp, dados FROM {safe_ident(self.tabela)} WHERE `timestamp` >= %s ORDER BY `timestamp` ASC"
#             rows = self.db.fetch_data(sql, (janela,))
            
#             if not rows:
#                 return {}

#             # Estruturas acumuladoras
#             # stats[slug_usina][nome_dispositivo] = { 'tempo_manutencao': 0, 'contagem': 0, 'em_manutencao': False }
#             stats = {}

#             for i in range(len(rows) - 1):
#                 atual = rows[i]
#                 proximo = rows[i+1]
                
#                 # Delta T em minutos
#                 dt_seconds = (proximo['timestamp'] - atual['timestamp']).total_seconds()
#                 dt_minutes = dt_seconds / 60.0
                
#                 # Evitar deltas gigantes (se o coletor ficou desligado 1 dia, não conta como manutenção)
#                 if dt_minutes > 60: 
#                     continue

#                 dados = atual['dados']
#                 if isinstance(dados, str):
#                     try:
#                         dados = json.loads(dados)
#                     except:
#                         continue
                
#                 # Estrutura do JSON: { 'usinas': [ { 'slug': '...', 'dispositivos': { ... } } ] }
#                 lista_usinas = dados.get('usinas', [])
                
#                 for usina in lista_usinas:
#                     slug = usina.get('slug')
#                     if not slug: continue
                    
#                     if slug not in stats: stats[slug] = {}
                    
#                     dispositivos = usina.get('dispositivos', {})
#                     for nome_disp, info in dispositivos.items():
#                         if nome_disp not in stats[slug]:
#                             stats[slug][nome_disp] = {'tempo_manutencao': 0.0, 'eventos': 0, 'ultimo_status_era_manutencao': False}
                        
#                         # Verifica status
#                         descricao = (info.get('descricao') or "").lower()
#                         em_manutencao = "manutenção" in descricao
                        
#                         # Contabiliza tempo
#                         if em_manutencao:
#                             stats[slug][nome_disp]['tempo_manutencao'] += dt_minutes
                            
#                         # Contabiliza eventos (borda de subida)
#                         if em_manutencao and not stats[slug][nome_disp]['ultimo_status_era_manutencao']:
#                             stats[slug][nome_disp]['eventos'] += 1
                            
#                         stats[slug][nome_disp]['ultimo_status_era_manutencao'] = em_manutencao

#             # Consolidar resultados por Usina
#             resultados = {}
#             for slug, disps in stats.items():
#                 tempo_total_usina = 0.0
#                 eventos_total_usina = 0
                
#                 for d in disps.values():
#                     tempo_total_usina += d['tempo_manutencao']
#                     eventos_total_usina += d['eventos']
                
#                 # MTTR da Usina (Média simples ou soma? Normalmente soma do tempo / soma dos eventos)
#                 mttr_minutos = 0
#                 if eventos_total_usina > 0:
#                     mttr_minutos = tempo_total_usina / eventos_total_usina
#                 elif tempo_total_usina > 0:
#                     # Se tem tempo mas não pegou o inicio do evento (evento veio de antes), considera 1 evento
#                     mttr_minutos = tempo_total_usina
                
#                 # Formatação amigável
#                 horas = int(mttr_minutos // 60)
#                 minutos = int(mttr_minutos % 60)
#                 mttr_str = f"{horas}h {minutos}m" if horas > 0 else f"{minutos} min"
                
#                 resultados[slug] = {
#                     'mttr_str': mttr_str if mttr_minutos > 0 else "0 min",
#                     'mttr_minutos': mttr_minutos,
#                     'eventos': eventos_total_usina
#                 }
                
#             return resultados

#         except Exception as e:
#             self._error('Read', 'get_indicadores_manutencao', e)
#             return {}


Labels de status:
    "UP (parada)",
    "UPGM (pronta para giro mecânico)",
    "UMD (marcha desexcitada)",
    "UPS (pronta para sincronização)",
    "US (sincronizado)",
    "Manutenção (parada)",
    "Restrição da concessionária (parada)",
    "Sem conexão",


A lógica segue a sequência de partida da máquina, lendo os "leds" virtuais presentes nos blocos centrais da imagem (U.P., U.P.G.M., U.M.D., U.P.S. e U.S.):

Aqui está a descrição completa:

1. U.P. (Parada) - Unidade Parada

   - A turbina está parada.
   - Unidade Hidráulica de Lubrificação dos Mancais (U.H.L.M.) está desligada.
   - Unidade Hidráulica de Regulação de Velocidade (U.H.R.V.) está desligada.
   - ByPass (de água) está fechado.
   - Válvula Borboleta da turbina está fechada.

2. U.P.G.M. (Pronta para Giro Mecânico) - Unidade Pronta para Giro Mecânico

   - U.H.L.M. está operacional (sistema de lubrificação ativo).
   - U.H.R.V. está operacional (sistema de regulação de velocidade ativo).
   - S.F.A. (Sistema de Filtragem de Água) está operacional.
   - Válvula Borboleta está aberta (permitindo a passagem de água até o distribuidor).
   - Turbina em estado operacional (condições de segurança satisfeitas para início do giro).

3. U.M.D. (Marcha Desexcitada) - Unidade em Marcha Desexcitada

   - R.V. (Regulador de Velocidade) Habilitado: O controle de velocidade da turbina está ativo.
   - Válv. Seg. Distribuidor: A Válvula de Segurança do Distribuidor está atuada/aberta.
   - Velocidade 90%: A turbina atingiu 90% da sua rotação nominal (mas ainda não há tensão nos terminais do gerador pois a excitação está desligada).

4. U.P.S. (Pronta para Sincronização) - Unidade Pronta para Sincronização

   - R.T. (Regulador de Tensão) Habilitado: O sistema de excitação foi ligado.
   - Tensão 90%: A tensão nos terminais do gerador atingiu 90% do valor nominal (a máquina já está gerando tensão, aguardando apenas o ajuste fino para sincronismo).
   - 5. U.S. (Sincronizado) - Unidade Sincronizada
   - Sincr. Habilitado: O relé ou sistema de sincronismo permitiu a operação.
   - Disj. 52G Fechado: O Disjuntor do Gerador (código ANSI 52) está fechado, conectando a usina à rede elétrica ou ao barramento de carga. A unidade está efetivamente gerando energia.

5. U.S. (Sincronizado) - Unidade Sincronizada

   - Sincr. Habilitado: O relé ou sistema de sincronismo permitiu a operação.
   - Disj. 52G Fechado: O Disjuntor do Gerador (código ANSI 52) está fechado, conectando a usina à rede elétrica ou ao barramento de carga. A unidade está efetivamente gerando energia.

6. Sem conexão

    Indica falha de comunicação entre o sistema de supervisão (a tela que estamos vendo) e o CLP (Controlador Lógico Programável) da usina. Neste estado, os valores mostrados na tela (geralmente representados por ####) não são confiáveis ou não estão sendo atualizados.

7. Manutenção

    Indica que a usina está em manutenção corretiva ou preventiva, parada para realizar troca de peças, reparos, etc.

8. Restrição da concessionária

    Indica que a usina está em restrição da concessionária, ou seja, está parada ou sem conexão devidos a eventos externos, geralmente interrompe a energia na linha e provoca o acionamento do gerador e proteções.

Para efeitos de procedimentos de rede do ONS, as categorias de parada a TEIF - Taxa de Indisponibilidade Forçada - são:

    1.Indisponibilidade Programada (IP): Manutenção preventiva agendada. (A usina não é penalizada se cumprir o prazo).
    2.Indisponibilidade Forçada (IF): Quebra, defeito ou trip. (A usina é penalizada).
    3.Indisponibilidade Externa: Linha de transmissão caiu, ONS mandou cortar geração. (Isenta de responsabilidade).
    4.Indisponibilidade Hidráulica: Falta de água ou cheia excessiva. (Isenta, mas precisa provar cota/nível).

Minha classificação inicial é uma cobertura generalista que vai justificar a classificação da ONS, no entanto, minha duvida e se a interface do softwaredeve cobrir esses procedimentos ou ele deve ser apresentado como informação de relatorio gerado pelo software.

Em todas as etapas de transição de status, exceto "Status sincronizado", devem ser calculados como usina parada, no entanto,
tenho que diferenciar esse verificação, por que as transições de status para efeito de analise de eficiência são etapas necessárias e de caracteristica de projeto.
Sendo assim, na interface de operação, tenho o MTTR (Tempo Médio de Parada), mas estou pensando em acrescentar um valor percentual para cada estado, e o MTTR ser um total não qualitativo.
Dai então, criar um outro indicador qualitativo, que desconsidera etapas necessarias de transição, desconsidera quando o nivel de água montante estiver abaixo do nivel de segurança ou quando a usina está desligada para aumentar o nível montante em níveis de retorno a operação. 

'''
'''
Aqui está minha análise técnica como Engenheiro de Software Sênior focado no domínio de hidrelétricas, baseada nos dados de log, na estrutura do `read.py` e na interface apresentada.

### 1. O Problema Conceitual do MTTR Atual
Na sua interface e lógica atual, qualquer estado diferente de "US (sincronizado)" parece estar penalizando o indicador de parada (MTTR). Isso é um erro conceitual grave para sistemas de energia.

*   **Transições (UPGM, UMD, UPS):** São etapas **operacionais**, não falhas. Uma máquina levar 5 minutos para sincronizar faz parte do *Tempo de Partida*, não do *Tempo de Reparo*.
*   **Restrição Hídrica (Nível Baixo):** Se a máquina para porque não tem água, a usina está **Disponível**, mas indisposta por recurso. Isso não deve contar como falha mecânica/elétrica.

### 2. Proposta de Novos Indicadores (Qualitativos)
Para resolver a questão levantada no `read.py` (linhas 306-309), sugiro separar o "tempo não produtivo" em três categorias distintas ("buckets") para o cálculo nos períodos (diário, semanal, etc):

#### A. Disponibilidade Física (Availability)
A métrica mais honesta para a manutenção.
*   **Fórmula:** `(Tempo Total - Tempo em Falha/Manutenção) / Tempo Total`
*   **Lógica:** Só penaliza se o status for "Sem conexão", "Erro" ou se houver um *flag* explícito de manutenção.
*   **Impacto:** Se a máquina está `UP (parada)` aguardando chuva, a disponibilidade é 100%.

#### B. Fator de Capacidade (Capacity Factor)
Métrica financeira/geração.
*   **Fórmula:** `Geração Real (MW médio) / Capacidade Instalada (MW)`
*   **Lógica:** Usa diretamente o sensor de "Potência Ativa".
*   **Impacto:** Mostra o quanto a usina está entregando do que ela foi projetada para entregar.

#### C. Eficiência de Partida (Startup Performance)
Métrica específica para as transições (UPGM → UMD → UPS → US).
*   **Conceito:** Monitorar a duração média que a UG fica nesses estados intermediários.
*   **Alerta:** Se o tempo médio de `UPS (pronta para sincronização)` começar a subir, indica problema no regulador de tensão ou no relé de sincronismo, antes mesmo de gerar uma falha.

### 3. Estratégia de Dados (Considerando o JSON atual)
Olhando seus logs (`3525-3643`), temos timestamps precisos e status por UG. Como uma usina tem N UGs (ex: PCH PEDRAS tem UG-01 e UG-02):

1.  **Cálculo Granular (Por UG):** Os indicadores devem ser calculados individualmente por UG. O indicador da Usina é a média ponderada (pela potência nominal) das UGs.
2.  **Detecção de "Parada Hídrica":**
    *   *Desafio:* O JSON atual não traz o "Nível Montante".
    *   *Solução Imediata:* Se `Status == UP` E `Erro == null`, classifique como **"Reserva Operacional"** (não penaliza MTTR).
    *   *Solução Ideal:* Adicionar leitura do nível no JSON e cruzar: `Se (Status == UP) AND (Nivel < Setpoint)`, então `Motivo = Hídrico`.

### 4. Resumo da Sugestão para a Interface
Substitua ou complemente o card único de "MTTR" por uma barra de composição (Stacked Bar) ou três KPIs menores:

1.  **Disponibilidade:** XX.X% (Tempo que a máquina *poderia* rodar).
2.  **Geração:** XX.X% (Tempo em `US`).
3.  **Reserva:** XX.X% (Tempo em `UP` sem erro + Transições).

**Conclusão:**
Mantenha o MTTR **apenas** para falhas reais (trips/erros). Crie um indicador separado chamado "Tempo em Reserva" para os momentos em que a usina está parada por decisão operacional ou falta de água. As transições devem ser somadas ao tempo de operação ou reserva, nunca ao tempo de reserva, nunca ao tempo de reserva, nunca ao tempo de prontidão, jamais como falha.


"Erro" ou se houver um flag explícito de manutenção.
    
'''