# Linha do Tempo Filtrada - Implementação

## ✅ O Que Foi Implementado

### 1. **Substituição da Timeline do Vertedouro**

A timeline específica do vertedouro foi substituída por uma **Timeline Filtrada** genérica e configurável que permite ao usuário filtrar ocorrências por múltiplos critérios.

---

## 🎯 Funcionalidades Implementadas

### **A. Filtros Disponíveis**

| Filtro | Tipo | Descrição |
|--------|------|-----------|
| **Tipo** | Select | Trip, Alarme, Evento, Manutenção, Comando |
| **Categoria** | Select | Operação/Humano, Elétrica, Hidráulica, Mecânica, Automação, Segurança, Ambiental |
| **Status** | Select | Aberta, Em Andamento, Resolvida, Cancelada |
| **Unidade** | Input Text | Busca em unidades e tags (ex: UG-01, Vertedouro, vibração) |

### **B. Controles de Filtragem**

1. **Botão "Aplicar Filtros"**: Executa a filtragem com os critérios selecionados
2. **Botão "Limpar"**: Remove todos os filtros e mostra todas as ocorrências
3. **Enter no campo Unidade**: Aplica filtros automaticamente
4. **Contador dinâmico**: Mostra quantas ocorrências correspondem aos filtros

### **C. Visualização com Scroll**

- **Altura máxima**: 600px
- **Altura mínima**: 200px
- **Scroll customizado**: Com estilização suave que respeita tema claro/escuro
- **Responsivo**: Adapta-se a diferentes tamanhos de tela

---

## 🎨 Interface e UX

### **Layout dos Filtros**
```
┌─────────────────────────────────────────────────────────────┐
│ Linha do Tempo: Filtrada                                    │
│ Filtrar ocorrências por critério                            │
├─────────────────────────────────────────────────────────────┤
│ [TIPO ▼]  [CATEGORIA ▼]  [STATUS ▼]  [UNIDADE/SISTEMA___] │
├─────────────────────────────────────────────────────────────┤
│ [Aplicar Filtros] [Limpar]                  X ocorrências   │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [•] Trip: Hidráulica - UG-01           [resolvida][alta]│ │
│ │     Descrição da ocorrência...                          │ │
│ │     14/10/2025, 12:30 por Humano                        │ │
│ │     [Resolver]                                          │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ [•] Alarme: Mecânica - UG-02      [em_andamento][média]│ │
│ │     Descrição...                                        │ │
│ │     ↓ SCROLL                                            │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Código de Cores**

#### Por Severidade:
- 🔴 **Alta/Crítica**: Vermelho (border-danger, bg-danger)
- 🟡 **Média**: Amarelo (border-warning, bg-warning)
- 🔵 **Baixa**: Azul (border-info, bg-info)

#### Por Status:
- 🟢 **Resolvida**: Verde
- 🔵 **Em Andamento**: Azul
- 🟡 **Aberta**: Amarelo
- ⚪ **Cancelada**: Cinza

---

## 💻 Implementação Técnica

### **1. HTML (usinas.html)**

#### Estrutura de Filtros:
```html
<!-- 4 filtros em grid responsivo -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
    <select id="filtro-tipo">...</select>
    <select id="filtro-categoria">...</select>
    <select id="filtro-status">...</select>
    <input id="filtro-unidade" type="text" />
</div>
```

#### Container com Scroll:
```html
<div class="max-h-[600px] min-h-[200px] overflow-y-auto custom-scrollbar">
    <!-- Itens de ocorrência -->
</div>
```

#### Data Attributes para Filtragem:
```html
<div class="ocorrencia-item"
     data-tipo="Trip"
     data-categoria="Hidráulica"
     data-status="resolvida"
     data-unidade="UG-01"
     data-tags="vibração,temperatura">
    <!-- Conteúdo -->
</div>
```

### **2. JavaScript (Inline no HTML)**

#### Função de Filtragem:
```javascript
function aplicarFiltros() {
    const filtroTipo = document.getElementById('filtro-tipo').value.toLowerCase();
    const filtroCategoria = document.getElementById('filtro-categoria').value.toLowerCase();
    const filtroStatus = document.getElementById('filtro-status').value.toLowerCase();
    const filtroUnidade = document.getElementById('filtro-unidade').value.toLowerCase();
    
    let contador = 0;
    
    ocorrenciasOriginais.forEach(item => {
        // Verificar cada filtro
        const passaTipo = !filtroTipo || item.dataset.tipo.toLowerCase().includes(filtroTipo);
        const passaCategoria = !filtroCategoria || item.dataset.categoria.toLowerCase().includes(filtroCategoria);
        const passaStatus = !filtroStatus || item.dataset.status.toLowerCase().includes(filtroStatus);
        const passaUnidade = !filtroUnidade || 
            item.dataset.unidade.toLowerCase().includes(filtroUnidade) || 
            item.dataset.tags.toLowerCase().includes(filtroUnidade);
        
        // Mostrar/ocultar item
        if (passaTipo && passaCategoria && passaStatus && passaUnidade) {
            item.style.display = 'flex';
            contador++;
        } else {
            item.style.display = 'none';
        }
    });
    
    // Atualizar contador
    document.getElementById('contador-filtrados').textContent = `${contador} ocorrências`;
}
```

### **3. CSS (styles.css)**

#### Scrollbar Customizado:
```css
.custom-scrollbar::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: var(--color-bg-alt);
    border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: var(--color-text-muted);
    border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: var(--color-text);
}
```

### **4. Controller (usinasController.py)**

#### Busca de Dados:
```python
# DEVELOPER MODE
timeline_vertedouro = get_ocorrencias_por_usina(usina['id'], limit=50)

# PRODUCTION MODE
timeline_vertedouro = self.ocorrencias.where(
    where={"usina_id": usina['id']},
    limit=50,
    order_by="created_at",
    desc=True
)
```

**Mudança importante**: Agora busca **TODAS** as ocorrências (não apenas alarmes ativos), permitindo filtragem completa.

---

## 🔍 Como Funciona a Filtragem

### **Lógica de Filtragem**

1. **Captura valores dos filtros** ao clicar em "Aplicar Filtros"
2. **Itera sobre todos os itens** de ocorrência (`.ocorrencia-item`)
3. **Verifica cada filtro**:
   - Se filtro está vazio → **passa** (não filtra)
   - Se filtro tem valor → verifica se o item corresponde
4. **Mostra/oculta** itens baseado em **AND lógico** (todos os filtros devem passar)
5. **Atualiza contador** com número de itens visíveis
6. **Mostra mensagem** "Nenhuma ocorrência encontrada" se contador = 0

### **Busca Flexível no Campo Unidade**

O campo "Unidade/Sistema" busca em dois lugares:
- **data-unidade**: Nome da unidade (ex: UG-01, Vertedouro)
- **data-tags**: Tags da ocorrência (ex: vibração, temperatura, nível)

Isso permite buscar por:
- Nome específico: "UG-01"
- Tipo de sistema: "Vertedouro"
- Tag/palavra-chave: "vibração", "temperatura"

---

## 📱 Responsividade

### Grid de Filtros:
- **Mobile** (< 768px): 1 coluna
- **Tablet** (768px - 1024px): 2 colunas
- **Desktop** (> 1024px): 4 colunas

### Container de Scroll:
- Altura ajusta automaticamente entre 200px e 600px
- Scroll aparece apenas quando necessário
- Touch-friendly em dispositivos móveis

---

## 🎯 Casos de Uso

### **1. Ver apenas alarmes ativos**
```
Tipo: [Todos]
Categoria: [Todos]
Status: [Aberta]
Unidade: []
```

### **2. Ver problemas elétricos**
```
Tipo: [Todos]
Categoria: [Elétrica]
Status: [Todos]
Unidade: []
```

### **3. Ver trips na UG-01**
```
Tipo: [Trip]
Categoria: [Todos]
Status: [Todos]
Unidade: [UG-01]
```

### **4. Ver ocorrências com vibração**
```
Tipo: [Todos]
Categoria: [Todos]
Status: [Todos]
Unidade: [vibração]
```

---

## ⚙️ Configurações

### **Limites de Busca**

No controller, ajuste o limite de ocorrências buscadas:

```python
# Mock (desenvolvimento)
timeline_vertedouro = get_ocorrencias_por_usina(usina['id'], limit=50)

# Real (produção)
timeline_vertedouro = self.ocorrencias.where(
    where={"usina_id": usina['id']},
    limit=50,  # Ajuste aqui
    order_by="created_at",
    desc=True
)
```

### **Altura do Container**

No HTML, ajuste as classes Tailwind:

```html
<div class="max-h-[600px] min-h-[200px] ...">
    <!-- max-h-[XXXpx]: altura máxima -->
    <!-- min-h-[XXXpx]: altura mínima -->
</div>
```

---

## 🚀 Melhorias Futuras

### **1. Filtros Avançados**
- Filtro por severidade (baixa, média, alta, crítica)
- Filtro por origem (humano, scada, api, importação)
- Filtro por período (últimas 24h, última semana, último mês)

### **2. Busca em Tempo Real**
- Filtrar conforme usuário digita (sem precisar clicar em "Aplicar")
- Debounce para performance

### **3. Salvar Filtros**
- Salvar combinações de filtros favoritas
- Carregar filtros salvos rapidamente

### **4. Exportar Resultados**
- Exportar ocorrências filtradas para CSV/Excel
- Gerar relatório PDF com filtros aplicados

### **5. Paginação**
- Adicionar paginação se houver muitas ocorrências
- Infinite scroll como alternativa

---

## ✅ Checklist de Teste

- [x] Filtro por Tipo funciona
- [x] Filtro por Categoria funciona
- [x] Filtro por Status funciona
- [x] Filtro por Unidade funciona
- [x] Busca em tags funciona
- [x] Botão "Aplicar Filtros" funciona
- [x] Botão "Limpar" funciona
- [x] Enter no campo Unidade aplica filtros
- [x] Contador atualiza corretamente
- [x] Scroll aparece quando necessário
- [x] Scrollbar customizado funciona
- [x] Responsivo em mobile/tablet/desktop
- [x] Mensagem "Nenhuma ocorrência" aparece quando vazio
- [ ] Testar com dados reais do banco
- [ ] Testar performance com muitas ocorrências (100+)
- [ ] Verificar acessibilidade (keyboard navigation)

---

## 📝 Notas Importantes

1. **Performance**: Com JavaScript client-side, a filtragem é instantânea para até ~100 itens. Para mais, considere filtragem server-side.

2. **Dados Reais**: Certifique-se de que o banco tem ocorrências variadas para testar todos os filtros.

3. **Compatibilidade**: Scrollbar customizado funciona em Chrome, Firefox, Safari e Edge modernos.

4. **Dark Mode**: Os estilos respeitam o tema escuro através das variáveis CSS.

5. **Acessibilidade**: Labels estão corretamente associados aos inputs para leitores de tela.

