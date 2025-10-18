# 📋 Guia de Migração - Resolução de Ocorrências

## ✅ Sistema Pronto para Uso (Modo Desenvolvedor)

O sistema já está configurado para usar dados mock automaticamente. Não é necessário conexão com banco de dados para testar!

**Status Atual:**
- ✅ `DEVELOPER_MODE = True` em `mock_data.py`
- ✅ Controllers configurados para não conectar ao banco
- ✅ 20 ocorrências mock com todos os campos necessários
- ✅ Interface HTML completa com tabs de registro e resolução

---

## 🗄️ Migrações do Banco de Dados

Quando estiver pronto para usar o banco de dados real, execute as migrações.

### Comandos Disponíveis

```bash
# Navegue até o diretório libs/models/docs
cd libs/models/docs

# 1. Migração Completa (Recomendado)
# Adiciona todos os campos, constraints e índices de uma vez
python cog_schema.py migrate

# 2. Adicionar Apenas os Campos
python cog_schema.py campos

# 3. Adicionar Apenas as Constraints
python cog_schema.py constraints

# 4. Adicionar Apenas os Índices
python cog_schema.py indices

# 5. Popular data_ocorrencia com created_at (Opcional)
# Útil se você já tem dados antigos no banco
python cog_schema.py populate

# 6. Criar Schema Original (5 tabelas)
python cog_schema.py schema
```

---

## 📦 O que Cada Migração Faz

### 1. **Campos** (`python cog_schema.py campos`)

Adiciona os seguintes campos na tabela `op_ocorrencia`:

| Campo | Tipo | Restrição | Descrição |
|-------|------|-----------|-----------|
| `requer_acao` | TINYINT(1) | NOT NULL DEFAULT 0 | Se requer ação urgente |
| `data_ocorrencia` | DATETIME(6) | NULL | Data/hora quando ocorreu |
| `resolvida_por` | BIGINT | NULL | ID do usuário que resolveu |
| `resolucao_descricao` | LONGTEXT | NULL | Como foi resolvida |

**SQL Executado:**
```sql
ALTER TABLE op_ocorrencia ADD COLUMN requer_acao TINYINT(1) NOT NULL DEFAULT 0;
ALTER TABLE op_ocorrencia ADD COLUMN data_ocorrencia DATETIME(6) NULL;
ALTER TABLE op_ocorrencia ADD COLUMN resolvida_por BIGINT NULL;
ALTER TABLE op_ocorrencia ADD COLUMN resolucao_descricao LONGTEXT NULL;
```

---

### 2. **Constraints** (`python cog_schema.py constraints`)

Adiciona foreign key para `resolvida_por`:

```sql
ALTER TABLE op_ocorrencia
ADD CONSTRAINT fk_oc_resolvedor 
FOREIGN KEY (resolvida_por) REFERENCES op_usuario(id)
ON DELETE SET NULL;
```

**Garante:**
- Integridade referencial
- Se usuário for deletado, o campo `resolvida_por` vira NULL (não quebra o histórico)

---

### 3. **Índices** (`python cog_schema.py indices`)

Adiciona índices para melhorar performance:

```sql
-- Índice composto para filtrar ocorrências que requerem ação
ALTER TABLE op_ocorrencia 
ADD INDEX ix_requer_acao (requer_acao, status);

-- Índice para ordenar por data de ocorrência
ALTER TABLE op_ocorrencia 
ADD INDEX ix_data_ocorrencia (data_ocorrencia);
```

**Benefícios:**
- ⚡ Consultas de ocorrências abertas/em andamento muito mais rápidas
- ⚡ Filtros por `requer_acao=true` otimizados
- ⚡ Ordenação por `data_ocorrencia` eficiente

---

### 4. **Popular Data** (`python cog_schema.py populate`)

Se você já tem ocorrências antigas sem `data_ocorrencia`, este comando copia o valor de `created_at`:

```sql
UPDATE op_ocorrencia 
SET data_ocorrencia = created_at 
WHERE data_ocorrencia IS NULL;
```

---

## 🔄 Processo Recomendado

### Para Desenvolvimento:

```bash
# 1. Use dados mock (já configurado!)
# Apenas execute: python main.py
python main.py
```

### Para Produção:

```bash
# 1. Certifique-se que o banco está acessível
# Verifique .env com credenciais corretas

# 2. Execute migração completa
cd libs/models/docs
python cog_schema.py migrate

# 3. (Opcional) Se já tem dados antigos, popular datas
python cog_schema.py populate

# 4. Desative modo desenvolvedor
# Edite libs/models/mock_data.py
# DEVELOPER_MODE = False

# 5. Inicie o sistema
python main.py
```

---

## ⚠️ Segurança

Todas as funções de migração:
- ✅ Verificam se campos/constraints/índices já existem
- ✅ Não fazem alterações duplicadas
- ✅ São seguras para executar múltiplas vezes
- ✅ Usam transações (commit apenas se tudo der certo)

---

## 🐛 Troubleshooting

### Erro: "Can't connect to MySQL server"

**Solução:**
```bash
# Verifique se DEVELOPER_MODE está True
# Edite libs/models/mock_data.py
DEVELOPER_MODE = True
```

### Erro: "Duplicate column name"

**Não é problema!** A migração detecta e pula campos que já existem.

### Erro: "Foreign key constraint fails"

**Causa:** Tabela `op_usuario` não existe ou não tem os dados necessários.

**Solução:**
```bash
# Crie o schema primeiro
python cog_schema.py schema

# Depois execute a migração
python cog_schema.py migrate
```

---

## 📊 Verificação Pós-Migração

```sql
-- Ver estrutura da tabela
DESCRIBE op_ocorrencia;

-- Ver índices
SHOW INDEX FROM op_ocorrencia;

-- Ver constraints
SELECT 
    CONSTRAINT_NAME, 
    TABLE_NAME, 
    REFERENCED_TABLE_NAME 
FROM 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE 
    TABLE_NAME = 'op_ocorrencia' 
    AND REFERENCED_TABLE_NAME IS NOT NULL;
```

---

## 📝 Notas

- **Tempo de Execução:** ~5-10 segundos para tabelas pequenas
- **Downtime:** Não requer parada do sistema (mas recomendado em produção)
- **Rollback:** Não implementado (faça backup antes!)
- **Compatibilidade:** MySQL 5.7+ ou MariaDB 10.2+

---

**Pronto! Sistema configurado para usar dados mock OU banco de dados real! 🚀**

