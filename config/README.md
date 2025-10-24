# Configurações de Usinas e Dispositivos

Este diretório contém as configurações de usinas e dispositivos para comunicação Modbus via VPN.

## Estrutura do Arquivo de Configuração

O arquivo `usinas_dispositivos.json` segue a seguinte estrutura:

```json
{
  "Nome da Usina": {
    "ip": "192.168.1.100",
    "port": 502,
    "table": "nome_tabela_banco",
    "dispositivos": {
      "Nome do Dispositivo": {
        "conexao": {
          "ip": "192.168.1.101",
          "port": 502
        },
        "caracteristicas": {
          "potência máxima": 100.5,
          "velocidade máxima": 1500
        },
        "leituras": {
          "REAL": {
            "potencia_ativa": 13407,
            "tensao_fase_a": 13408
          },
          "INT": {
            "frequencia": 13500
          }
        },
        "temperaturas": {
          "REAL": {
            "temp_mancal_superior": 14000,
            "temp_mancal_inferior": 14001
          },
          "INT": {}
        },
        "alarmes": {
          "BOOLEAN": {
            "alarme_vibracao": 24289,
            "alarme_temperatura": 24290
          }
        },
        "comandos": {
          "BOOLEAN": {
            "comando_ligar": 12529,
            "comando_desligar": 12530
          }
        }
      }
    }
  }
}
```

## Campos Obrigatórios

### Usina
- **ip**: Endereço IP da API da usina
- **port**: Porta de comunicação com a API da usina
- **table**: Nome da tabela no banco de dados (opcional)
- **dispositivos**: Deve conter pelo menos 1 dispositivo

### Dispositivo
- **conexao.ip**: Endereço IP do dispositivo Modbus
- **conexao.port**: Porta de comunicação Modbus do dispositivo

## Campos Opcionais

- **caracteristicas**: Propriedades do dispositivo (potência, velocidade, etc.)
- **leituras**: Endereços Modbus para leitura de valores (REAL, INT)
- **temperaturas**: Endereços Modbus para leitura de temperaturas (REAL, INT)
- **alarmes**: Endereços Modbus para leitura de alarmes (BOOLEAN)
- **comandos**: Endereços Modbus para envio de comandos (BOOLEAN)

## Tipos de Dados

- **REAL**: Valores em ponto flutuante (float)
- **INT**: Valores inteiros
- **BOOLEAN**: Valores binários (0 ou 1)

## Observações

- Uma usina pode ter múltiplos dispositivos
- Cada dispositivo tem seu próprio IP e porta para comunicação Modbus
- Os endereços Modbus são valores inteiros que representam os registros a serem lidos/escritos
- As características podem ser qualquer propriedade relevante do dispositivo
- Se um tipo de entrada (leituras, alarmes, etc.) não for utilizado, pode ser omitido ou deixado vazio

## Interface de Configuração

Para configurar usinas e dispositivos através da interface web, acesse:
```
http://localhost:5000/configuracoes
```

A interface permite:
- Adicionar/remover usinas
- Adicionar/remover dispositivos por usina
- Configurar IPs e portas
- Adicionar características personalizadas
- Configurar entradas de leitura, alarmes, temperaturas e comandos
- Visualizar e copiar o JSON gerado
- Salvar a configuração no servidor

