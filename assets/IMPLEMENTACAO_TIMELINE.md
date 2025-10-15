# Implementação das Timelines de Ocorrências

## 📋 O Que Foi Implementado

### 1. **Funções no `mock_data.py`**

Foram criadas três novas funções para buscar ocorrências específicas de uma usina:

#### `get_ocorrencias_por_usina(usina_id, limit=10)`
- **Objetivo**: Retorna todas as ocorrências de uma usina específica
- **Uso**: Timeline Geral (mostra todas as ocorrências da usina)
- **Retorno**: Lista de ocorrências ordenadas por data (mais recente primeiro)

#### `get_alarmes_ativos_usina(usina_id, categorias=None, limit=5)`
- **Objetivo**: Retorna apenas alarmes ATIVOS (status: aberta ou em_andamento)
- **Uso**: Base para a timeline do vertedouro
- **Filtros**: Pode filtrar por categorias específicas
- **Retorno**: Lista de alarmes ativos ordenados por data

#### `get_timeline_vertedouro(usina_id, limit=5)`
- **Objetivo**: Retorna alarmes relacionados ao vertedouro
- **Uso**: Timeline do Vertedouro (alarmes de Hidráulica, Automação, Ambiental)
- **Retorno**: Lista de alarmes filtrados por categoria

---

### 2. **Atualização do `usinasController.py`**

#### **Modo DEVELOPER (Mock)**
```python
timeline_geral = get_ocorrencias_por_usina(usina['id'], limit=10)
timeline_vertedouro = get_timeline_vertedouro(usina['id'], limit=5)
```

#### **Modo PRODUÇÃO (Banco Real)**
```python
# Timeline Geral - Todas as ocorrências da usina
timeline_geral = self.ocorrencias.where(
    where={"usina_id": usina['id']}, 
    limit=10,
    order_by="created_at",
    desc=True
)

# Timeline Vertedouro - Alarmes ativos específicos
timeline_vertedouro = self.ocorrencias.where(
    where={
        "usina_id": usina['id'],
        "status__in": ["aberta", "em_andamento"],
        "categoria__in": ["Hidráulica", "Automação", "Ambiental"]
    },
    limit=5,
    order_by="created_at",
    desc=True
)
```

---

### 3. **Atualização do `usinas.html`**

#### **Timeline do Vertedouro (Alarmes Ativos)**
- Mostra apenas alarmes com status "aberta" ou "em_andamento"
- Código de cores por severidade:
  - 🔴 **Alta/Crítica**: vermelho
  - 🟡 **Média**: amarelo/warning
  - 🔵 **Baixa**: azul/info
- Exibe:
  - Tipo e categoria do alarme
  - Badge de severidade
  - Descrição resumida (150 caracteres)
  - Data e origem
  - Tags (se houver)
  - Botão "Resolver"

#### **Timeline Geral (Todas as Ocorrências)**
- Mostra todas as ocorrências da usina (resolvidas ou não)
- Código de cores por status:
  - 🟢 **Resolvida**: verde
  - 🔵 **Em andamento**: azul
  - 🟡 **Aberta**: amarelo
  - ⚪ **Cancelada**: cinza
- Exibe:
  - Categoria e status
  - Tipo, unidade e descrição resumida (100 caracteres)
  - Data de criação e resolução (se resolvida)

---

## 🎯 O Que é Necessário para Implementar com Dados Reais

### 1. **Verificar a Estrutura do Banco de Dados**

Confirme que a tabela `op_ocorrencia` possui todos os campos necessários:

```sql
-- Campos obrigatórios para as timelines
SELECT 
    id,
    usina_id,
    operador_id,
    tipo,
    categoria,
    unidade,
    descricao,
    status,              -- 'aberta', 'em_andamento', 'resolvida', 'cancelada'
    severidade,          -- 'baixa', 'média', 'alta', 'crítica'
    origem,              -- 'humano', 'scada', 'api', 'importacao'
    tags,                -- CSV de tags
    created_at,
    updated_at,
    resolved_at
FROM op_ocorrencia
LIMIT 1;
```

### 2. **Testar as Queries do Banco Real**

#### **Teste 1: Buscar ocorrências de uma usina**
```sql
SELECT * FROM op_ocorrencia 
WHERE usina_id = 1 
ORDER BY created_at DESC 
LIMIT 10;
```

#### **Teste 2: Buscar alarmes ativos por categoria**
```sql
SELECT * FROM op_ocorrencia 
WHERE usina_id = 1 
  AND status IN ('aberta', 'em_andamento')
  AND categoria IN ('Hidráulica', 'Automação', 'Ambiental')
ORDER BY created_at DESC 
LIMIT 5;
```

### 3. **Verificar Operadores da Classe Read**

O código usa operadores avançados do modelo `Read`. Confirme que estão implementados:

```python
# Operador __in para múltiplos valores
where={
    "status__in": ["aberta", "em_andamento"],
    "categoria__in": ["Hidráulica", "Automação", "Ambiental"]
}
```

Se o operador `__in` não existir, você precisará:
- Implementá-lo na classe `Read` em `libs/models/read.py`
- Ou fazer múltiplas queries e combinar os resultados

### 4. **Criar Ocorrências de Teste**

Para testar as timelines adequadamente, crie ocorrências com diferentes status:

```sql
-- Alarme ativo para testar timeline do vertedouro
INSERT INTO op_ocorrencia (
    usina_id, operador_id, tipo, categoria, unidade,
    descricao, status, severidade, origem, created_at
) VALUES (
    1, 1, 'Alarme', 'Hidráulica', 'Vertedouro',
    'Nível de montante acima do limite operacional', 
    'aberta', 'média', 'scada', NOW()
);

-- Ocorrência resolvida para timeline geral
INSERT INTO op_ocorrencia (
    usina_id, operador_id, tipo, categoria, unidade,
    descricao, status, severidade, origem, 
    created_at, resolved_at
) VALUES (
    1, 2, 'Manutenção', 'Mecânica', 'UG-01',
    'Manutenção preventiva dos mancais', 
    'resolvida', 'baixa', 'humano', 
    '2025-10-13 08:00:00', '2025-10-13 12:00:00'
);
```

### 5. **Validar Formatação de Datas no Template**

O template usa `strftime()` para formatar datas. Certifique-se de que:
- O campo `created_at` retorna um objeto `datetime` (não string)
- O campo `resolved_at` pode ser `None` para ocorrências não resolvidas

Se as datas vierem como string do banco, você precisará convertê-las:

```python
# No controller, após buscar os dados
for ocorrencia in timeline_geral:
    if isinstance(ocorrencia['created_at'], str):
        ocorrencia['created_at'] = datetime.strptime(
            ocorrencia['created_at'], 
            '%Y-%m-%d %H:%M:%S'
        )
```

### 6. **Padronizar Nomenclatura de Unidades**

Verifique inconsistências no campo `unidade`:
- "CGH PICADAS ALTAS" vs "CGH-PICADAS ALTAS"
- "PCH-PEDRAS" vs "PCG PEDRAS"

Crie uma função de normalização ou atualize o banco:

```sql
-- Padronizar nomes de unidades
UPDATE op_ocorrencia 
SET unidade = 'CGH-PICADAS ALTAS' 
WHERE unidade = 'CGH PICADAS ALTAS';

UPDATE op_ocorrencia 
SET unidade = 'PCH-PEDRAS' 
WHERE unidade IN ('PCG PEDRAS', 'PCH PEDRAS');
```

---

## 🧪 Como Testar

### 1. **Testar com Dados Mock (DEVELOPER_MODE = True)**
```python
# Em libs/models/mock_data.py
DEVELOPER_MODE = True
```
- Acesse: `http://localhost:5000/usinas/APAR`
- Verifique se as timelines aparecem corretamente
- Teste com diferentes siglas (APAR, FAE, HOPP, PICALT, PEDR)

### 2. **Testar com Dados Reais (DEVELOPER_MODE = False)**
```python
# Em libs/models/mock_data.py
DEVELOPER_MODE = False
```
- Verifique os logs no console para ver os dados retornados
- Confirme que `timeline_geral` e `timeline_vertedouro` têm dados
- Teste se as formatações de data funcionam

### 3. **Verificar Console de Debug**
O controller imprime os dados no console:
```
--------------------------------
timeline_geral
[{...}, {...}]
--------------------------------
timeline_vertedouro
[{...}, {...}]
--------------------------------
```

---

## 📊 Estrutura de Dados Esperada

### Timeline Geral (Ocorrências)
```python
[
    {
        'id': 20,
        'usina_id': 1,
        'tipo': 'Trip',
        'categoria': 'Hidráulica',
        'unidade': 'CGH-APARECIDA',
        'descricao': 'Descrição detalhada...',
        'status': 'resolvida',
        'severidade': 'alta',
        'origem': 'humano',
        'tags': 'vibração,temperatura',
        'created_at': datetime(2025, 10, 14, 10, 30),
        'resolved_at': datetime(2025, 10, 14, 11, 15)
    }
]
```

### Timeline Vertedouro (Alarmes Ativos)
```python
[
    {
        'id': 10,
        'usina_id': 1,
        'tipo': 'Alarme',
        'categoria': 'Hidráulica',
        'unidade': 'Vertedouro',
        'descricao': 'Nível acima do limite...',
        'status': 'aberta',  # ou 'em_andamento'
        'severidade': 'média',
        'origem': 'scada',
        'tags': 'nivel,montante',
        'created_at': datetime(2025, 10, 14, 10, 30),
        'resolved_at': None
    }
]
```

---

## 🔄 Próximos Passos

1. **Implementar operador `__in`** na classe `Read` se não existir
2. **Criar script de seed** para popular ocorrências de teste
3. **Validar queries** com dados reais do banco
4. **Testar performance** com grande volume de ocorrências
5. **Implementar paginação** se necessário (atualmente limit=10 e limit=5)
6. **Adicionar filtros** por data, tipo, severidade, etc.
7. **Implementar botão "Resolver"** para mudar status de alarmes

---

## 🎨 Customizações Possíveis

### Adicionar Mais Categorias no Vertedouro
```python
# Em mock_data.py ou no controller
timeline_vertedouro = get_alarmes_ativos_usina(
    usina_id, 
    categorias=['Hidráulica', 'Automação', 'Ambiental', 'Elétrica'],
    limit=5
)
```

### Filtrar por Período de Tempo
```python
# Adicionar filtro de data
from datetime import datetime, timedelta

timeline_geral = self.ocorrencias.where(
    where={
        "usina_id": usina['id'],
        "created_at__gte": datetime.now() - timedelta(days=7)  # últimos 7 dias
    },
    limit=10,
    order_by="created_at",
    desc=True
)
```

### Adicionar Contadores
```python
# No controller
total_alarmes_ativos = len(timeline_vertedouro)
total_ocorrencias = len(timeline_geral)

# Passar para o template
return render_template(
    "usinas.html",
    # ...
    total_alarmes_ativos=total_alarmes_ativos,
    total_ocorrencias=total_ocorrencias
)
```

---

## ✅ Checklist de Implementação

- [x] Criar funções no `mock_data.py`
- [x] Atualizar `usinasController.py` com lógica mock e real
- [x] Atualizar `usinas.html` com templates dinâmicos
- [ ] Verificar operador `__in` na classe `Read`
- [ ] Testar queries com banco de dados real
- [ ] Criar ocorrências de teste no banco
- [ ] Validar formatação de datas
- [ ] Padronizar nomenclatura de unidades
- [ ] Testar com DEVELOPER_MODE = False
- [ ] Implementar funcionalidade do botão "Resolver"
- [ ] Adicionar paginação se necessário

---

## 🐛 Possíveis Problemas e Soluções

### Problema 1: Operador `__in` não existe
**Solução**: Implementar na classe `Read` ou usar múltiplas queries

### Problema 2: Datas vêm como string
**Solução**: Converter para `datetime` no controller

### Problema 3: Nenhuma ocorrência aparece
**Solução**: Verificar se `usina_id` está correto e se há ocorrências no banco

### Problema 4: Template quebra com erro de formatação
**Solução**: Adicionar verificação `if` antes de usar `strftime()`

### Problema 5: Timeline vertedouro sempre vazia
**Solução**: Criar alarmes com status 'aberta' ou 'em_andamento' no banco

