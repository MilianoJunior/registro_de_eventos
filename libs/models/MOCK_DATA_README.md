# Documentação do Sistema de Mock Data

## Visão Geral

O arquivo `mock_data.py` centraliza todos os dados simulados (mock) para a fase de desenvolvimento, permitindo que os desenvolvedores trabalhem sem necessidade de conexão com o banco de dados.

## Como Usar

### 1. Ativar/Desativar Modo Desenvolvedor

Edite o arquivo `libs/models/mock_data.py` e altere a variável:

```python
DEVELOPER_MODE = True  # Ativar modo desenvolvedor (usa dados mock)
DEVELOPER_MODE = False # Desativar (usa dados reais do banco)
```

### 2. Estrutura dos Dados

O arquivo contém dados mock para todas as tabelas do sistema:

- **MOCK_USINAS**: Lista de usinas cadastradas
- **MOCK_USUARIOS**: Lista de usuários do sistema
- **MOCK_OCORRENCIAS**: Lista de ocorrências registradas
- **MOCK_OCORRENCIA_HIST**: Histórico de alterações nas ocorrências
- **MOCK_ANEXOS**: Anexos vinculados às ocorrências

### 3. Funções Auxiliares

#### `get_mock_data(table_name)`
Retorna os dados mock de uma tabela específica.

```python
from libs.models.mock_data import get_mock_data

usinas = get_mock_data('op_usina')
usuarios = get_mock_data('op_usuario')
```

#### `get_usina_by_sigla(sigla)`
Retorna uma usina específica pela sigla.

```python
from libs.models.mock_data import get_usina_by_sigla

usina = get_usina_by_sigla('APAR')  # CGH-APARECIDA
```

#### `get_ocorrencias_recentes(limit=10)`
Retorna as ocorrências mais recentes (ordenadas por data).

```python
from libs.models.mock_data import get_ocorrencias_recentes

recentes = get_ocorrencias_recentes(limit=5)
```

#### `get_estatisticas_home()`
Retorna um dicionário completo com todas as estatísticas para a página home.

```python
from libs.models.mock_data import get_estatisticas_home

stats = get_estatisticas_home()
# Retorna: {
#     'recentes': [...],
#     'status': Counter(...),
#     'unidades': Counter(...),
#     'por_unidade': [...],
#     'usinas': [...],
#     'total_ocorrencias': int
# }
```

## Controllers Atualizados

Todos os controllers foram atualizados para suportar o modo desenvolvedor:

### HomeController
```python
if DEVELOPER_MODE:
    stats = get_estatisticas_home()
    usinas = stats['usinas']
    recentes = stats['recentes']
    # ... usa dados mock
else:
    # ... usa dados do banco
```

### UsinasController
```python
if DEVELOPER_MODE:
    usina = get_usina_by_sigla(sigla)
else:
    usina = self.usinas.first({"sigla": sigla})
```

### EventosController
```python
if DEVELOPER_MODE:
    usinas = get_mock_data('op_usina')
    usuarios = get_mock_data('op_usuario')
else:
    usinas = self.usinas.get_all()
    usuarios = self.usuarios.get_all()
```

## Adicionar Novos Dados Mock

Para adicionar novos registros mock, edite o arquivo `mock_data.py` e adicione itens às listas correspondentes:

```python
MOCK_USINAS.append({
    'id': 6,
    'nome': 'CGH-NOVA',
    'sigla': 'NOVA',
    'timezone': 'America/Sao_Paulo',
    'ativo': 1,
    'created_at': datetime(2025, 10, 1, 10, 0, 0),
    'updated_at': datetime(2025, 10, 1, 10, 0, 0)
})
```

## Importante

⚠️ **Antes de ir para produção:**
1. Altere `DEVELOPER_MODE = False` no arquivo `mock_data.py`
2. Teste todas as funcionalidades com dados reais
3. Verifique se todas as consultas ao banco estão funcionando corretamente

## Benefícios

✅ Desenvolvimento mais rápido sem dependência de banco de dados  
✅ Dados consistentes entre desenvolvedores  
✅ Facilita testes e demonstrações  
✅ Código limpo e organizado  
✅ Fácil transição entre desenvolvimento e produção  

