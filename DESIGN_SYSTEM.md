# 🎨 Sistema de Design Padronizado

## 📋 Visão Geral

Todos os componentes agora usam as variáveis CSS definidas em `variables.css`, permitindo alterações dinâmicas em todo o projeto através da modificação das variáveis.

## 🎯 Componentes Disponíveis

### 1. Card Component
```html
{% from "components/_macros.html" import card %}

{% call card("Título do Card", with_css=True) %}
  <div class="chips">
    <span class="chip">Item 1</span>
    <span class="chip">Item 2</span>
  </div>
  <div class="muted">Texto secundário</div>
{% endcall %}
```

### 2. Button Component
```html
{% from "components/_macros.html" import button %}

<!-- Botão primário -->
{{ button("Salvar", "primary", "md", "submit", False, True) }}

<!-- Botão de sucesso pequeno -->
{{ button("Confirmar", "success", "sm", "button", False, True) }}

<!-- Botão de perigo grande -->
{{ button("Excluir", "danger", "lg", "button", False, True) }}
```

**Variantes disponíveis:**
- `primary` - Azul (padrão)
- `success` - Verde
- `warning` - Amarelo
- `danger` - Vermelho
- `secondary` - Cinza

**Tamanhos disponíveis:**
- `sm` - Pequeno
- `md` - Médio (padrão)
- `lg` - Grande

### 3. Input Component
```html
{% from "components/_macros.html" import input %}

{{ input("Nome", "nome", "text", "Digite seu nome", "", True, True) }}
{{ input("Email", "email", "email", "seu@email.com", "", True, True) }}
{{ input("Senha", "senha", "password", "", "", True, True) }}
```

## 🎨 Variáveis CSS Principais

### Cores
```css
--color-bg: #0f172a;        /* Fundo principal */
--color-bg-alt: #111827;    /* Fundo de cards */
--color-surface: #1f2937;   /* Camadas acima */
--color-text: #e5e7eb;      /* Texto principal */
--color-text-muted: #94a3b8; /* Texto secundário */
--color-accent: #3b82f6;    /* Azul principal */
--color-success: #22c55e;   /* Verde */
--color-warning: #eab308;   /* Amarelo */
--color-danger: #ef4444;   /* Vermelho */
```

### Espaçamentos
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem; /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem; /* 20px */
--space-6: 1.5rem;  /* 24px */
```

### Tipografia
```css
--font-size-xs: 0.75rem;   /* 12px */
--font-size-sm: 0.875rem;  /* 14px */
--font-size-md: 1rem;      /* 16px */
--font-size-lg: 1.125rem;  /* 18px */
--font-size-xl: 1.25rem;   /* 20px */
```

### Bordas e Raios
```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-full: 9999px;
```

## 🔄 Como Alterar o Tema Dinamicamente

Para alterar o tema de todo o projeto, basta modificar as variáveis em `variables.css`:

```css
:root {
  /* Mudança de tema claro para escuro */
  --color-bg: #ffffff;        /* Fundo branco */
  --color-bg-alt: #f8fafc;   /* Fundo de cards claro */
  --color-text: #1e293b;     /* Texto escuro */
  --color-text-muted: #64748b; /* Texto secundário */
}
```

## 📱 Responsividade

O sistema inclui breakpoints responsivos:
```css
--container-sm: 640px;
--container-md: 768px;
--container-lg: 1024px;
--container-xl: 1280px;
```

## 🎯 Classes Utilitárias

### Grid Layout
```html
<div class="grid">
  <!-- Cards se organizam automaticamente em grid responsivo -->
</div>
```

### Chips
```html
<div class="chips">
  <span class="chip">Tag 1</span>
  <span class="chip">Tag 2</span>
</div>
```

### Lista Compacta
```html
<ul class="list-compact">
  <li>Item 1</li>
  <li>Item 2</li>
</ul>
```

### Tabela Limpa
```html
<table class="clean">
  <tbody>
    <tr>
      <td>Nome</td>
      <td>Valor</td>
    </tr>
  </tbody>
</table>
```

## ✨ Benefícios

1. **Consistência Visual**: Todos os componentes seguem o mesmo padrão
2. **Manutenibilidade**: Alterações centralizadas em `variables.css`
3. **Flexibilidade**: Fácil criação de temas personalizados
4. **Responsividade**: Layout adaptável a diferentes telas
5. **Acessibilidade**: Contraste e tamanhos adequados
