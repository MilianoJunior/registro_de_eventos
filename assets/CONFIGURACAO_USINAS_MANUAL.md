# Manual de Uso: Interface de Configuração de Usinas e Dispositivos

## Visão Geral

A interface de configuração permite gerenciar as usinas e seus dispositivos para comunicação Modbus via VPN. A configuração é feita de forma hierárquica: **Usinas → Dispositivos → Entradas**.

## Acessando a Interface

1. Abra o navegador e acesse: `http://localhost:5000/configuracoes`
2. A interface carregará automaticamente qualquer configuração existente
3. Se não houver configuração, uma usina vazia será criada automaticamente

## Estrutura Hierárquica

```
Usina
├── IP e Porta da API
├── Nome da Tabela (opcional)
└── Dispositivos (mínimo 1)
    ├── Nome do Dispositivo
    ├── IP e Porta Modbus
    ├── Características (opcional)
    │   ├── Potência Máxima
    │   ├── Velocidade Máxima
    │   └── Outras características personalizadas
    └── Entradas de Comunicação (opcional)
        ├── Leituras (REAL, INT)
        ├── Temperaturas (REAL, INT)
        ├── Alarmes (BOOLEAN)
        └── Comandos (BOOLEAN)
```

## Passo a Passo

### 1. Adicionar uma Usina

1. Clique no botão **"Nova Usina"** no canto superior direito
2. Preencha os campos:
   - **Nome da Usina**: Ex: "CGH APARECIDA"
   - **IP da Usina**: Endereço IP da API da usina (Ex: 192.168.1.100)
   - **Porta**: Porta de comunicação com a API (Ex: 502)
   - **Nome da Tabela**: Nome da tabela no banco de dados (opcional)

### 2. Adicionar Dispositivos

1. Cada usina precisa ter **pelo menos 1 dispositivo**
2. Clique em **"+ Dispositivo"** dentro da seção de dispositivos da usina
3. Preencha os campos:
   - **Nome do Dispositivo**: Ex: "UG-01", "Turbina Principal"
   - **IP do Dispositivo**: Endereço IP do CLP/Dispositivo Modbus
   - **Porta**: Porta de comunicação Modbus (geralmente 502)

### 3. Configurar Características do Dispositivo

As características são propriedades do dispositivo que podem ser usadas como referência:

1. **Características Padrão**: 
   - Potência Máxima: Valor em kW (Ex: 1000.0)
   
2. **Características Personalizadas**:
   - Clique em **"+ Característica"**
   - Digite o nome (Ex: "vazao_maxima")
   - Digite o valor (Ex: 10.5)
   - Adicione quantas características precisar

### 4. Configurar Entradas de Comunicação

#### Leituras
Valores que serão lidos do dispositivo (potência, tensão, corrente, etc.):

1. Clique em **"Adicionar"** na seção "Leituras"
2. Selecione o **Tipo**:
   - **REAL**: Para valores decimais (float)
   - **INT**: Para valores inteiros
3. Digite o **Nome**: Ex: "potencia_ativa"
4. Digite o **Endereço**: Endereço Modbus (Ex: 13407)

#### Temperaturas
Valores de temperatura dos componentes:

1. Clique em **"Adicionar"** na seção "Temperaturas"
2. Funciona igual às leituras
3. Ex: "temp_mancal_superior" → Endereço: 14000

#### Alarmes
Estados binários de alarmes do dispositivo:

1. Clique em **"Adicionar"** na seção "Alarmes"
2. Tipo será sempre **BOOLEAN**
3. Ex: "alarme_vibracao" → Endereço: 24289

#### Comandos
Comandos que podem ser enviados ao dispositivo:

1. Clique em **"Adicionar"** na seção "Comandos"
2. Tipo será sempre **BOOLEAN**
3. Ex: "comando_ligar" → Endereço: 12529

### 5. Expandir/Recolher Seções

- Clique no ícone de seta (▼) ao lado do nome da usina para expandir/recolher
- Isso ajuda a organizar quando há muitas usinas configuradas

### 6. Remover Itens

- **Remover Entrada**: Clique no **X** ao lado da entrada
- **Remover Dispositivo**: Clique no ícone de lixeira 🗑️ ao lado do nome
- **Remover Usina**: Clique no ícone de lixeira 🗑️ no cabeçalho da usina
- **Limpar Tudo**: Clique no botão **"Limpar Tudo"** (remove todas as configurações)

### 7. Visualizar Configuração

1. Clique no botão **"Visualizar JSON"**
2. Uma janela modal mostrará a configuração em formato JSON
3. Você pode:
   - **Copiar JSON**: Copiar para a área de transferência
   - **Fechar**: Fechar a visualização

### 8. Salvar Configuração

1. Clique no botão **"Salvar Configuração"**
2. O sistema validará:
   - Se há pelo menos uma usina
   - Se cada usina tem pelo menos um dispositivo
   - Se os campos obrigatórios estão preenchidos
3. Uma notificação aparecerá indicando:
   - ✅ **Sucesso**: "Configuração salva com sucesso! X usina(s) configurada(s)"
   - ⚠️ **Aviso**: Mensagem indicando o que falta preencher
   - ❌ **Erro**: Mensagem de erro caso ocorra algum problema

## Validações

### Campos Obrigatórios:

**Usina:**
- Nome da Usina
- IP da Usina
- Porta da Usina
- Pelo menos 1 dispositivo

**Dispositivo:**
- Nome do Dispositivo
- IP do Dispositivo
- Porta do Dispositivo

**Entradas (se adicionadas):**
- Tipo (REAL, INT ou BOOLEAN)
- Nome da entrada
- Endereço Modbus

### Campos Opcionais:
- Nome da Tabela
- Características
- Leituras, Temperaturas, Alarmes, Comandos (podem estar vazios)

## Dicas de Uso

1. **Organização**: Use nomes descritivos para usinas e dispositivos (Ex: "CGH APARECIDA", "UG-01")

2. **Endereços Modbus**: 
   - Verifique a documentação do dispositivo para os endereços corretos
   - Endereços geralmente são números de 4 ou 5 dígitos

3. **Tipos de Dados**:
   - Use **REAL** para valores com casas decimais (1000.5, 13.7)
   - Use **INT** para valores inteiros (100, 1500)
   - Use **BOOLEAN** para valores binários (0/1, ligado/desligado)

4. **Múltiplas Usinas**: 
   - Você pode adicionar quantas usinas precisar
   - Use o accordion para expandir/recolher e manter organizado

5. **Backup**: 
   - Use "Visualizar JSON" e "Copiar JSON" para fazer backup manual
   - O arquivo é salvo em `config/usinas_dispositivos.json`

## Arquivo de Configuração

A configuração é salva no arquivo:
```
config/usinas_dispositivos.json
```

Você também pode editar esse arquivo manualmente se preferir. Veja o arquivo de exemplo em:
```
config/usinas_dispositivos.exemplo.json
```

## Notificações

A interface usa notificações coloridas para feedback:

- 🔵 **Azul (Info)**: Informações gerais
- 🟢 **Verde (Sucesso)**: Operação realizada com sucesso
- 🟡 **Amarelo (Aviso)**: Atenção necessária
- 🔴 **Vermelho (Erro)**: Erro que precisa ser corrigido

## Teclas de Atalho

- **Enter** no formulário: Salvar configuração
- **Esc**: Fechar modal de visualização

## Solução de Problemas

### "Por favor, adicione pelo menos uma usina"
- Clique em "Nova Usina" e preencha os campos obrigatórios

### "A usina X precisa ter pelo menos um dispositivo"
- Adicione pelo menos um dispositivo à usina mencionada

### "Erro ao salvar configuração"
- Verifique se todos os campos obrigatórios estão preenchidos
- Verifique a conexão com o servidor
- Veja o console do navegador (F12) para mais detalhes

### Configuração não carrega
- Verifique se o arquivo existe em `config/usinas_dispositivos.json`
- Verifique se o arquivo tem formato JSON válido
- Veja o console do navegador (F12) para erros

## Próximos Passos

Após configurar as usinas e dispositivos:

1. As configurações podem ser usadas pelo sistema de leitura Modbus
2. As tabelas mencionadas podem ser criadas no banco de dados
3. As leituras podem ser visualizadas na interface principal
4. Os comandos podem ser enviados através da interface de controle

## Suporte

Para mais informações sobre a estrutura de dados, consulte:
- `config/README.md` - Documentação da estrutura de configuração
- `config/usinas_dispositivos.exemplo.json` - Exemplo de configuração completa

