# Plano de Melhorias - Registro de Ocorrências

## 📋 ANÁLISE DO CÓDIGO ATUAL

### ✅ O Que Está Funcionando

**1. Controller (`eventosController.py`)**
- ✅ Validação de campos obrigatórios (linhas 91-94)
- ✅ Preparação dos dados para inserção (linhas 97-110)
- ✅ Status padrão: `"aberta"` (linha 107)
- ✅ Origem: `"humano"` (linha 109)
- ✅ Retorna ID do registro criado (linha 119)

**2. Model Create (`create.py`)**
- ✅ Método `insert()` bem estruturado
- ✅ Usa prepared statements (segurança SQL injection)
- ✅ Retorna `lastrowid` (ID do registro inserido)
- ✅ Tratamento de erros

**3. Estrutura da Tabela**
```sql
op_ocorrencia:
- usina_id ✅
- operador_id ✅
- tipo ✅
- categoria ✅
- unidade ✅
- tags ✅
- playbook ✅
- template_texto ✅
- descricao ✅
- status ✅ (aberta|em_andamento|resolvida|cancelada)
- severidade ✅ (baixa|média|alta|crítica)
- origem ✅ (humano|scada|api|importacao)
- metadata ✅ (JSON)
- created_at ✅ (auto)
- updated_at ✅ (auto)
- resolved_at ✅ (nullable)
```

### ⚠️ Possíveis Problemas

**1. Modo DEVELOPER está ativo**
```python
# libs/models/mock_data.py
DEVELOPER_MODE = True  # ← Não está salvando no banco!
```
**Solução**: Alterar para `False` para salvar no banco real

**2. Falta de feedback visual**
- Não há mensagem de sucesso/erro no frontend
- Não redireciona após salvar
- Não limpa o formulário

**3. Campo `metadata` não está sendo usado**
- Pode ser usado para flags especiais (ex: "requer_acao")

---

## 🎯 IMPLEMENTAÇÕES NECESSÁRIAS

### **1. Adicionar Campo "Requer Ação/Notificação"**

#### A. Nova Checkbox no Formulário HTML

```html
<!-- Adicionar após severidade -->
<div>
    <label class="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" id="requer_acao" name="requer_acao" 
               class="w-4 h-4 rounded border-slate-300 text-danger focus:ring-danger">
        <span class="text-sm font-medium text-text-primary">
            ⚠️ Requer Ação Urgente
        </span>
    </label>
    <p class="text-xs text-text-muted mt-1 ml-6">
        Marque se esta ocorrência precisa de atenção imediata da equipe
    </p>
</div>
```

#### B. Atualizar Controller para Salvar Flag

```python
# eventosController.py - criar_ocorrencia()
ocorrencia_data = {
    # ... campos existentes ...
    "metadata": json.dumps({
        "requer_acao": data.get("requer_acao", False),
        "notificado_em": None,
        "responsavel_id": None
    })
}
```

#### C. Badge Visual nas Listas

```html
{% if ocorrencia.metadata and ocorrencia.metadata.get('requer_acao') %}
    <span class="px-2 py-1 bg-danger/10 text-danger text-xs font-medium rounded flex items-center gap-1">
        <span class="material-icons text-sm">warning</span>
        REQUER AÇÃO
    </span>
{% endif %}
```

#### D. Botão de Ação

```html
{% if ocorrencia.metadata and ocorrencia.metadata.get('requer_acao') 
     and ocorrencia.status != 'resolvida' %}
    <button onclick="assumirResponsabilidade({{ ocorrencia.id }})" 
            class="px-3 py-1.5 bg-danger text-white text-xs rounded hover:opacity-90">
        Assumir Responsabilidade
    </button>
{% endif %}
```

---

### **2. Uniformizar Nomenclatura**

#### Arquivos que Precisam de Mudança:

| Arquivo | Linha/Local | Mudança |
|---------|-------------|---------|
| `_sidebar.html` | 13-15 | "Registrar Evento" → "Registrar Ocorrência" |
| `registro_eventos.html` | 3, 7 | Título e heading |
| `routes.py` | Nome da rota | `registro_eventos` → `registro_ocorrencias` |
| `eventosController.py` | 16, 76 | Comentários e strings |
| `readme.md` | Vários | Atualizar documentação |
| `FLOWCHART.md` | Vários | Atualizar diagramas |

#### Nomenclatura Padronizada:

| Antigo | Novo |
|--------|------|
| Evento | Ocorrência |
| Registrar Evento | Registrar Ocorrência |
| registro_eventos | registro_ocorrencias |
| EventosController | OcorrenciasController |

---

## 🚀 PLANO DE IMPLEMENTAÇÃO

### **FASE 1: Verificação e Testes (Você faz)**

- [ ] Alterar `DEVELOPER_MODE = False` em `mock_data.py`
- [ ] Tentar registrar uma ocorrência
- [ ] Verificar se aparece no banco: `SELECT * FROM op_ocorrencia ORDER BY id DESC LIMIT 1`
- [ ] Verificar logs no console para errors
- [ ] Testar se todos os campos estão sendo salvos

**Se NÃO salvar:**
- Verificar logs de erro no terminal Flask
- Verificar conexão com banco (`libs/models/database.py`)
- Verificar se tabela `op_ocorrencia` existe
- Verificar se campos da tabela correspondem ao código

---

### **FASE 2: Adicionar Campo "Requer Ação" (Eu implemento)**

**2.1. Frontend - HTML**
- [ ] Adicionar checkbox "Requer Ação Urgente"
- [ ] Adicionar descrição explicativa
- [ ] Estilizar checkbox com Tailwind

**2.2. Frontend - JavaScript**
- [ ] Capturar valor do checkbox no submit
- [ ] Adicionar ao payload JSON
- [ ] Mostrar confirmação se marcado

**2.3. Backend - Controller**
- [ ] Atualizar `criar_ocorrencia()` para receber `requer_acao`
- [ ] Salvar no campo `metadata` como JSON
- [ ] Validar tipo boolean

**2.4. Visualização**
- [ ] Adicionar badge "REQUER AÇÃO" nas listas
- [ ] Destacar visualmente (vermelho/warning)
- [ ] Adicionar ícone de alerta

**2.5. Funcionalidade de Ação**
- [ ] Botão "Assumir Responsabilidade"
- [ ] Endpoint para atualizar responsável
- [ ] Notificação no dashboard
- [ ] Filtro especial para "Requer Ação"

---

### **FASE 3: Uniformizar Nomenclatura (Eu implemento)**

**3.1. Views**
- [ ] `_sidebar.html`: "Registrar Evento" → "Registrar Ocorrência"
- [ ] `registro_eventos.html`: Título e headings
- [ ] `home.html`: Referências a eventos

**3.2. Routes**
- [ ] `routes.py`: Manter compatibilidade ou criar redirect
- [ ] Atualizar endpoint `registro_eventos` → `registro_ocorrencias`

**3.3. Controllers**
- [ ] Renomear `eventosController.py` → `ocorrenciasController.py`
- [ ] Atualizar classe `EventosController` → `OcorrenciasController`
- [ ] Atualizar comentários

**3.4. Documentação**
- [ ] `readme.md`: Atualizar referências
- [ ] `FLOWCHART.md`: Atualizar diagramas
- [ ] Criar migration guide se necessário

---

## 📊 ESTRUTURA DE DADOS - Metadata JSON

### Formato Proposto:

```json
{
  "requer_acao": true,
  "prioridade_adicional": "urgente",
  "notificado_em": "2025-10-14T15:30:00",
  "notificados": [1, 3, 5],  // IDs dos usuários notificados
  "responsavel_id": 2,        // ID do usuário que assumiu
  "assumido_em": "2025-10-14T16:00:00",
  "observacoes": "Requer inspeção física imediata",
  "equipamento_parado": true,
  "impacto_geracao": true
}
```

### Uso em Queries:

```python
# Buscar ocorrências que requerem ação
where={
    "status__in": ["aberta", "em_andamento"],
    "metadata__like": "%requer_acao%: true%"
}

# Ou melhor ainda, criar campo específico:
ALTER TABLE op_ocorrencia ADD COLUMN requer_acao BOOLEAN DEFAULT FALSE;
```

---

## 🔧 MELHORIAS ADICIONAIS (Opcionais)

### **1. Notificações Push**
- Socket.IO para notificações em tempo real
- Badge de contador no sidebar
- Som de alerta opcional

### **2. Workflow de Resolução**
```
ABERTA → [Assumir] → EM_ANDAMENTO → [Resolver] → RESOLVIDA
         └─ requer_acao=true marca como urgente
```

### **3. SLA/Tempo de Resposta**
```python
# Se requer_acao=true, calcular tempo desde criação
tempo_decorrido = now() - created_at
if tempo_decorrido > 2h:
    status_sla = "ATRASADO"
```

### **4. Dashboard de Alertas**
- Card especial para "Ocorrências Urgentes"
- Lista filtrada automaticamente
- Cores de destaque (vermelho)

---

## 🧪 TESTES A REALIZAR

### **1. Teste de Salvamento**
```python
# Test script
from libs.controllers.eventosController import EventosController

controller = EventosController()
test_data = {
    "usina_id": 1,
    "operador_id": 1,
    "tipo": "Alarme",
    "categoria": "Elétrica",
    "unidade": "UG-01",
    "tags": "teste",
    "descricao": "Teste de salvamento",
    "severidade": "média",
    "requer_acao": True
}

# Simular request POST
result = controller.criar_ocorrencia()
print(result)  # Deve retornar ID e success=True
```

### **2. Teste de Visualização**
- Criar ocorrência com `requer_acao=True`
- Verificar se badge aparece
- Verificar se botão "Assumir" aparece
- Verificar ordenação (urgentes primeiro?)

### **3. Teste de Performance**
- Criar 100 ocorrências
- Verificar tempo de carregamento
- Verificar se connection pool está funcionando

---

## ✅ CHECKLIST DE VALIDAÇÃO

**Salvamento no Banco:**
- [ ] `DEVELOPER_MODE = False`
- [ ] Ocorrências aparecem na tabela
- [ ] Todos os campos preenchidos corretamente
- [ ] `created_at` e `updated_at` automáticos
- [ ] ID retornado corretamente

**Campo "Requer Ação":**
- [ ] Checkbox aparece no formulário
- [ ] Valor é capturado e enviado
- [ ] Salvo no campo `metadata` (ou coluna própria)
- [ ] Badge aparece nas listagens
- [ ] Botão de ação funciona
- [ ] Filtro de urgentes funciona

**Nomenclatura:**
- [ ] Todos textos atualizados
- [ ] Rotas atualizadas (com backward compatibility)
- [ ] Controllers renomeados
- [ ] Documentação atualizada
- [ ] Sem referências a "eventos" (exceto contextuais)

---

## 📝 PRÓXIMOS PASSOS

1. **VOCÊ**: Teste o salvamento alterando `DEVELOPER_MODE = False`
2. **VOCÊ**: Reporte se está salvando ou quais erros aparecem
3. **EU**: Implemento campo "Requer Ação"
4. **EU**: Uniformizo nomenclatura
5. **AMBOS**: Testamos tudo funcionando

---

Aguardando seu feedback sobre o teste de salvamento! 🚀

