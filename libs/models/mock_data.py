# libs/models/mock_data.py
"""
Dados mocados para fase de desenvolvimento
Define DEVELOPER_MODE = True para usar dados mock em todos os controllers
"""
from datetime import datetime
from collections import Counter

# ============================================================
# CONFIGURAÇÃO GLOBAL DE DESENVOLVIMENTO
# ============================================================
DEVELOPER_MODE = False # Alterar para False em produção


# ============================================================
# TABELA: op_usina
# ============================================================
MOCK_USINAS = [
    {
        'id': 1, 
        'nome': 'CGH-APARECIDA', 
        'sigla': 'APAR', 
        'timezone': 'America/Sao_Paulo', 
        'ativo': 1,
        'status_operacional': 'operando',
        'potencia_ativa_mw': 1200,
        'mttr': '13h min',
        'alarmes_por_hora': 8.00,
        'alarmes_criticos': 0,
        'incidentes_abertos': 1,
        'alarmes_atencao': 3,
        'alarmes_inundantes': 0,
        'alarmes_oscilantes': 2,
        'energia_nao_gerada_mwh': 0,
        'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0},
        'created_at': datetime(2025, 9, 23, 14, 28, 29, 150993), 
        'updated_at': datetime(2025, 9, 23, 21, 21, 11, 659664)
    },
    {
        'id': 2, 
        'nome': 'CGH-FAE', 
        'sigla': 'FAE', 
        'timezone': 'America/Sao_Paulo', 
        'ativo': 1,
        'status_operacional': 'operando',
        'potencia_ativa_mw': 950,
        'mttr': '8h min',
        'alarmes_por_hora': 5.20,
        'alarmes_criticos': 0,
        'incidentes_abertos': 0,
        'alarmes_atencao': 1,
        'alarmes_inundantes': 0,
        'alarmes_oscilantes': 0,
        'energia_nao_gerada_mwh': 0,
        'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0},
        'created_at': datetime(2025, 9, 23, 14, 28, 29, 354315), 
        'updated_at': datetime(2025, 9, 23, 14, 28, 29, 354315)
    },
    {
        'id': 3, 
        'nome': 'CGH-HOPPEN', 
        'sigla': 'HOPP', 
        'timezone': 'America/Sao_Paulo', 
        'ativo': 1,
        'status_operacional': 'operando',
        'potencia_ativa_mw': 850,
        'mttr': '20 min',
        'alarmes_por_hora': 0.21,
        'alarmes_criticos': 0,
        'incidentes_abertos': 0,
        'alarmes_atencao': 2,
        'alarmes_inundantes': 0,
        'alarmes_oscilantes': 1,
        'energia_nao_gerada_mwh': 0,
        'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0},
        'created_at': datetime(2025, 9, 23, 14, 28, 29, 558514), 
        'updated_at': datetime(2025, 9, 23, 14, 28, 29, 558514)
    },
    {
        'id': 4, 
        'nome': 'CGH-PICADAS ALTAS', 
        'sigla': 'PICALT', 
        'timezone': 'America/Sao_Paulo', 
        'ativo': 1,
        'status_operacional': 'manutencao',
        'potencia_ativa_mw': 0,
        'mttr': 'N/A',
        'alarmes_por_hora': 0,
        'alarmes_criticos': 1,
        'incidentes_abertos': 1,
        'alarmes_atencao': 0,
        'alarmes_inundantes': 0,
        'alarmes_oscilantes': 0,
        'energia_nao_gerada_mwh': 120,
        'distribuicao_prioridade': {'alta': 100, 'media': 0, 'baixa': 0},
        'created_at': datetime(2025, 9, 23, 14, 28, 29, 766481), 
        'updated_at': datetime(2025, 9, 23, 14, 28, 29, 766481)
    },
    {
        'id': 5, 
        'nome': 'PCH-PEDRAS', 
        'sigla': 'PEDR', 
        'timezone': 'America/Sao_Paulo', 
        'ativo': 1,
        'status_operacional': 'operando',
        'potencia_ativa_mw': 1150,
        'mttr': '10h min',
        'alarmes_por_hora': 3.45,
        'alarmes_criticos': 0,
        'incidentes_abertos': 0,
        'alarmes_atencao': 1,
        'alarmes_inundantes': 0,
        'alarmes_oscilantes': 0,
        'energia_nao_gerada_mwh': 0,
        'distribuicao_prioridade': {'alta': 0, 'media': 100, 'baixa': 0},
        'created_at': datetime(2025, 9, 23, 14, 28, 29, 969718), 
        'updated_at': datetime(2025, 9, 23, 14, 28, 29, 969718)
    }
]


# ============================================================
# TABELA: op_usuario
# ============================================================
MOCK_USUARIOS = [
    {
        'id': 1,
        'nome': 'João Silva',
        'email': 'joao.silva@engegom.com.br',
        'perfil': 'operador',
        'ativo': 1,
        'created_at': datetime(2025, 9, 20, 8, 0, 0),
        'updated_at': datetime(2025, 9, 20, 8, 0, 0)
    },
    {
        'id': 2,
        'nome': 'Maria Santos',
        'email': 'maria.santos@engegom.com.br',
        'perfil': 'engenharia',
        'ativo': 1,
        'created_at': datetime(2025, 9, 20, 8, 15, 0),
        'updated_at': datetime(2025, 9, 20, 8, 15, 0)
    },
    {
        'id': 3,
        'nome': 'Carlos Oliveira',
        'email': 'carlos.oliveira@engegom.com.br',
        'perfil': 'operador',
        'ativo': 1,
        'created_at': datetime(2025, 9, 20, 8, 30, 0),
        'updated_at': datetime(2025, 9, 20, 8, 30, 0)
    },
    {
        'id': 4,
        'nome': 'Ana Costa',
        'email': 'ana.costa@engegom.com.br',
        'perfil': 'gestor',
        'ativo': 1,
        'created_at': datetime(2025, 9, 20, 8, 45, 0),
        'updated_at': datetime(2025, 9, 20, 8, 45, 0)
    },
    {
        'id': 5,
        'nome': 'Pedro Almeida',
        'email': 'pedro.almeida@engegom.com.br',
        'perfil': 'admin',
        'ativo': 1,
        'created_at': datetime(2025, 9, 20, 9, 0, 0),
        'updated_at': datetime(2025, 9, 20, 9, 0, 0)
    }
]


# ============================================================
# TABELA: op_ocorrencia
# ============================================================
MOCK_OCORRENCIAS = [
    {
        'id': 20, 
        'usina_id': 5, 
        'operador_id': 3, 
        'tipo': 'Trip', 
        'categoria': 'Hidráulica', 
        'unidade': 'PCH-PEDRAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: UG-01 Gerador - Temperatura alta mancal - LNA - Guia - Trip\nResultado: Religamento das unidades UG-01\nObservação: Após verificar que as temperatura estavam dentro dos números aceitavéis e a parada total da unidade geradora, foi possivel fazer o religamento da mesma.', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 12, 2, 4), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 55), 
        'resolved_at': datetime(2025, 7, 12, 2, 4)
    },
    {
        'id': 19, 
        'usina_id': 4, 
        'operador_id': 3, 
        'tipo': 'Trip', 
        'categoria': 'Hidráulica', 
        'unidade': 'CGH PICADAS ALTAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 11, 0, 52), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 54), 
        'resolved_at': datetime(2025, 7, 11, 0, 52)
    },
    {
        'id': 18, 
        'usina_id': 4, 
        'operador_id': 3, 
        'tipo': 'Evento', 
        'categoria': 'Elétrica', 
        'unidade': 'CGH PICADAS ALTAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico e eletrico\nCondição: PSA - Disjuntor de linha 52L - Falha de fechamento\nResultado: Religamento das unidades UG-01 e UG-02\nObservação: Após trip das unidades geradora, foi realizadio o fechamento do disjuntor de linha 52L, e o religamento das unidades geradoras.', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 10, 22, 15), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 53), 
        'resolved_at': datetime(2025, 7, 10, 22, 15)
    },
    {
        'id': 17, 
        'usina_id': 5, 
        'operador_id': 1, 
        'tipo': 'Trip', 
        'categoria': 'Hidráulica', 
        'unidade': 'PCG PEDRAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: UG-01 - Turbina - Bucha Radial 01 - Trip\nResultado: Religamento da unidade UG-01\nObservação: Após trip da unidade geradora, foi feito o religamento', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 10, 18, 23), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 52), 
        'resolved_at': datetime(2025, 7, 10, 18, 23)
    },
    {
        'id': 16, 
        'usina_id': 3, 
        'operador_id': 3, 
        'tipo': 'Trip', 
        'categoria': 'Elétrica', 
        'unidade': 'CGH HOPPEN', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: UG-01 Relé de proteção - Sobretensão Fase e Neutro\nCondição: UG-01 em Trip\nResultado: Religamento da unidade UG-01\nObservação: Após trip da unidade geradora, foi feito o religamento', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 10, 6, 11), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 51), 
        'resolved_at': datetime(2025, 7, 10, 6, 11)
    },
    {
        'id': 15, 
        'usina_id': 4, 
        'operador_id': 3, 
        'tipo': 'Trip', 
        'categoria': 'Hidráulica', 
        'unidade': 'CGH PICADAS ALTAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 10, 2, 26), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 49), 
        'resolved_at': datetime(2025, 7, 10, 2, 26)
    },
    {
        'id': 14, 
        'usina_id': 4, 
        'operador_id': 1, 
        'tipo': 'Trip', 
        'categoria': 'Hidráulica', 
        'unidade': 'CGH PICADAS ALTAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 9, 19, 40), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 47), 
        'resolved_at': datetime(2025, 7, 9, 19, 40)
    },
    {
        'id': 13, 
        'usina_id': 4, 
        'operador_id': 3, 
        'tipo': 'Trip', 
        'categoria': 'Hidráulica', 
        'unidade': 'CGH PICADAS ALTAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 9, 3, 5), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 46), 
        'resolved_at': datetime(2025, 7, 9, 3, 5)
    },
    {
        'id': 12, 
        'usina_id': 5, 
        'operador_id': 4, 
        'tipo': 'Trip', 
        'categoria': 'Operação/Humano', 
        'unidade': 'PCH-PEDRAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Partir a UG-02 após um TRIP\nCondição: UG02-UHLM - Ausência fluxo de Oleo 04 - Verificar fluxostasto\nResultado: Não é possível partir a UG-02', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 9, 3, 0), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 45), 
        'resolved_at': datetime(2025, 7, 9, 3, 0)
    },
    {
        'id': 11, 
        'usina_id': 4, 
        'operador_id': 3, 
        'tipo': 'Trip', 
        'categoria': 'Hidráulica', 
        'unidade': 'CGH PICADAS ALTAS', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Operação: Relé de bloqueio 86H ativado-Bloqueio Hidráulico-Trip UG-01\nCondição: Nívle de desligamento 415.85 m\nResultado: Parada da unidade pela falta de água na montante\nObservação: O controle de religamento está ativo, portanto quando o nível de água da montante for estabelecido nos valores configurados ela retorna a operação.', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 8, 22, 14), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 44), 
        'resolved_at': datetime(2025, 7, 8, 22, 14)
    },
    {
        'id': 10, 
        'usina_id': 1, 
        'operador_id': 2, 
        'tipo': 'Alarme', 
        'categoria': 'Mecânica', 
        'unidade': 'CGH-APARECIDA', 
        'tags': 'vibração', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Alarme de vibração excessiva detectado na UG-01. Nível de vibração: 8.5mm/s. Limite: 7.0mm/s.\nEquipe de manutenção acionada para inspeção.', 
        'status': 'em_andamento', 
        'severidade': 'média', 
        'origem': 'scada', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 7, 14, 30), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 43), 
        'resolved_at': None
    },
    {
        'id': 9, 
        'usina_id': 2, 
        'operador_id': 1, 
        'tipo': 'Manutenção', 
        'categoria': 'Elétrica', 
        'unidade': 'CGH-FAE', 
        'tags': 'preventiva', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Manutenção preventiva programada - Substituição de filtros do sistema de refrigeração.\nParada programada das 08h às 12h.', 
        'status': 'resolvida', 
        'severidade': 'baixa', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 5, 8, 0), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 42), 
        'resolved_at': datetime(2025, 7, 5, 12, 15)
    },
    {
        'id': 8, 
        'usina_id': 3, 
        'operador_id': 3, 
        'tipo': 'Evento', 
        'categoria': 'Automação', 
        'unidade': 'CGH HOPPEN', 
        'tags': 'scada', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Perda de comunicação com o SCADA por 15 minutos. Comunicação restabelecida automaticamente.\nNenhuma operação foi afetada durante o período.', 
        'status': 'resolvida', 
        'severidade': 'média', 
        'origem': 'scada', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 3, 10, 45), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 41), 
        'resolved_at': datetime(2025, 7, 3, 11, 0)
    },
    {
        'id': 7, 
        'usina_id': 1, 
        'operador_id': 2, 
        'tipo': 'Alarme', 
        'categoria': 'Hidráulica', 
        'unidade': 'CGH-APARECIDA', 
        'tags': 'nivel', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Nível do reservatório abaixo do ideal. Nível atual: 414.20m. Nível mínimo operacional: 414.50m.\nMonitoramento intensificado.', 
        'status': 'aberta', 
        'severidade': 'média', 
        'origem': 'scada', 
        'metadata': None, 
        'created_at': datetime(2025, 7, 1, 6, 15), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 40), 
        'resolved_at': None
    },
    {
        'id': 6, 
        'usina_id': 2, 
        'operador_id': 4, 
        'tipo': 'Comando', 
        'categoria': 'Operação/Humano', 
        'unidade': 'CGH-FAE', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Comando manual de abertura da comporta vertedouro executado devido ao aumento do nível do reservatório.\nAbertura: 30%. Vazão: 15m³/s.', 
        'status': 'resolvida', 
        'severidade': 'baixa', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 6, 28, 16, 20), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 39), 
        'resolved_at': datetime(2025, 6, 28, 18, 0)
    },
    {
        'id': 5, 
        'usina_id': 4, 
        'operador_id': 1, 
        'tipo': 'Trip', 
        'categoria': 'Elétrica', 
        'unidade': 'CGH-PICADAS ALTAS', 
        'tags': 'sobrecarga', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Trip por sobrecarga no gerador. Corrente medida: 520A. Limite: 500A.\nUnidade desligada automaticamente. Inspeção realizada, sem danos identificados.\nReligamento bem-sucedido.', 
        'status': 'resolvida', 
        'severidade': 'alta', 
        'origem': 'scada', 
        'metadata': None, 
        'created_at': datetime(2025, 6, 25, 22, 10), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 38), 
        'resolved_at': datetime(2025, 6, 25, 23, 45)
    },
    {
        'id': 4, 
        'usina_id': 5, 
        'operador_id': 3, 
        'tipo': 'Evento', 
        'categoria': 'Ambiental', 
        'unidade': 'PCH-PEDRAS', 
        'tags': 'vazão', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Vazão ecológica monitorada e dentro dos parâmetros estabelecidos pelo órgão ambiental.\nVazão atual: 2.8m³/s. Vazão mínima exigida: 2.5m³/s.', 
        'status': 'resolvida', 
        'severidade': 'baixa', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 6, 22, 9, 0), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 37), 
        'resolved_at': datetime(2025, 6, 22, 9, 15)
    },
    {
        'id': 3, 
        'usina_id': 3, 
        'operador_id': 2, 
        'tipo': 'Manutenção', 
        'categoria': 'Mecânica', 
        'unidade': 'CGH HOPPEN', 
        'tags': 'preventiva,lubrificação', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Manutenção preventiva - Lubrificação dos mancais da turbina.\nTroca de óleo hidráulico realizada conforme cronograma.\nSistema testado e aprovado.', 
        'status': 'resolvida', 
        'severidade': 'baixa', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 6, 18, 7, 30), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 36), 
        'resolved_at': datetime(2025, 6, 18, 11, 45)
    },
    {
        'id': 2, 
        'usina_id': 1, 
        'operador_id': 4, 
        'tipo': 'Alarme', 
        'categoria': 'Elétrica', 
        'unidade': 'CGH-APARECIDA', 
        'tags': 'temperatura', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Alarme de temperatura elevada nos enrolamentos do gerador.\nTemperatura: 95°C. Limite: 90°C.\nCarga reduzida em 10% para normalização da temperatura.', 
        'status': 'resolvida', 
        'severidade': 'média', 
        'origem': 'scada', 
        'metadata': None, 
        'created_at': datetime(2025, 6, 15, 14, 20), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 35), 
        'resolved_at': datetime(2025, 6, 15, 15, 30)
    },
    {
        'id': 1, 
        'usina_id': 2, 
        'operador_id': 1, 
        'tipo': 'Comando', 
        'categoria': 'Operação/Humano', 
        'unidade': 'CGH-FAE', 
        'tags': '', 
        'playbook': None, 
        'template_texto': None, 
        'descricao': 'Sincronização da UG-02 com a rede realizada com sucesso.\nFrequência: 60.0Hz, Tensão: 13.8kV, Sincronismo perfeito.\nUnidade em operação nominal.', 
        'status': 'resolvida', 
        'severidade': 'baixa', 
        'origem': 'humano', 
        'metadata': None, 
        'created_at': datetime(2025, 6, 10, 8, 45), 
        'updated_at': datetime(2025, 9, 12, 19, 55, 34), 
        'resolved_at': datetime(2025, 6, 10, 9, 0)
    }
]


# ============================================================
# TABELA: op_ocorrencia_hist
# ============================================================
MOCK_OCORRENCIA_HIST = [
    {
        'id': 1,
        'ocorrencia_id': 1,
        'usuario_id': 1,
        'acao': 'criado',
        'detalhe': '{"status": "aberta"}',
        'created_at': datetime(2025, 6, 10, 8, 45, 0)
    },
    {
        'id': 2,
        'ocorrencia_id': 1,
        'usuario_id': 1,
        'acao': 'status',
        'detalhe': '{"de": "aberta", "para": "resolvida"}',
        'created_at': datetime(2025, 6, 10, 9, 0, 0)
    },
    {
        'id': 3,
        'ocorrencia_id': 2,
        'usuario_id': 4,
        'acao': 'criado',
        'detalhe': '{"status": "aberta"}',
        'created_at': datetime(2025, 6, 15, 14, 20, 0)
    },
    {
        'id': 4,
        'ocorrencia_id': 2,
        'usuario_id': 4,
        'acao': 'comentario',
        'detalhe': 'Temperatura normalizada após redução de carga',
        'created_at': datetime(2025, 6, 15, 15, 30, 0)
    }
]


# ============================================================
# TABELA: op_anexo
# ============================================================
MOCK_ANEXOS = [
    {
        'id': 1,
        'ocorrencia_id': 2,
        'nome_arquivo': 'grafico_temperatura.png',
        'mime_type': 'image/png',
        'tamanho_bytes': 245680,
        'url_armazenamento': '/uploads/ocorrencias/2/grafico_temperatura.png',
        'created_by': 4,
        'created_at': datetime(2025, 6, 15, 15, 0, 0)
    },
    {
        'id': 2,
        'ocorrencia_id': 3,
        'nome_arquivo': 'checklist_manutencao.pdf',
        'mime_type': 'application/pdf',
        'tamanho_bytes': 1024000,
        'url_armazenamento': '/uploads/ocorrencias/3/checklist_manutencao.pdf',
        'created_by': 2,
        'created_at': datetime(2025, 6, 18, 11, 45, 0)
    },
    {
        'id': 3,
        'ocorrencia_id': 10,
        'nome_arquivo': 'relatorio_vibracao.xlsx',
        'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'tamanho_bytes': 512000,
        'url_armazenamento': '/uploads/ocorrencias/10/relatorio_vibracao.xlsx',
        'created_by': 2,
        'created_at': datetime(2025, 7, 7, 15, 0, 0)
    }
]


# ============================================================
# FUNÇÕES AUXILIARES PARA CONTROLLERS
# ============================================================

def get_mock_data(table_name):
    """Retorna os dados mock da tabela especificada"""
    data_map = {
        'op_usina': MOCK_USINAS,
        'op_usuario': MOCK_USUARIOS,
        'op_ocorrencia': MOCK_OCORRENCIAS,
        'op_ocorrencia_hist': MOCK_OCORRENCIA_HIST,
        'op_anexo': MOCK_ANEXOS
    }
    return data_map.get(table_name, [])


def get_usina_by_sigla(sigla):
    """Retorna uma usina específica pela sigla"""
    for usina in MOCK_USINAS:
        if usina['sigla'] == sigla:
            return usina
    return None


def get_ocorrencias_recentes(limit=10):
    """Retorna as ocorrências mais recentes"""
    return sorted(MOCK_OCORRENCIAS, key=lambda r: r.get("created_at"), reverse=True)[:limit]


def get_estatisticas_home():
    """Retorna estatísticas para a página home"""
    rows = MOCK_OCORRENCIAS
    
    recentes = sorted(rows, key=lambda r: r.get("created_at"), reverse=True)[:10]
    status = Counter((r.get("status") or "-") for r in rows)
    unidades = Counter((r.get("unidade") or "-") for r in rows)
    por_unidade = sorted(unidades.items(), key=lambda x: (-x[1], x[0]))[:8]
    
    # Calcula a potência ativa total das usinas operando
    potencia_total = sum(u.get('potencia_ativa_mw', 0) for u in MOCK_USINAS if u.get('status_operacional') == 'operando')
    
    return {
        'recentes': recentes,
        'status': status,
        'unidades': unidades,
        'por_unidade': por_unidade,
        'usinas': MOCK_USINAS,
        'total_ocorrencias': len(rows),
        'potencia_total_mw': potencia_total
    }


def get_ocorrencias_por_usina(usina_id, limit=10):
    """
    Retorna ocorrências de uma usina específica ordenadas por data
    
    Args:
        usina_id: ID da usina
        limit: Número máximo de ocorrências a retornar
    
    Returns:
        Lista de ocorrências da usina ordenadas por created_at (mais recente primeiro)
    """
    ocorrencias_usina = [
        ocorrencia for ocorrencia in MOCK_OCORRENCIAS 
        if ocorrencia.get('usina_id') == usina_id
    ]
    
    return sorted(ocorrencias_usina, key=lambda r: r.get("created_at"), reverse=True)[:limit]


def get_alarmes_ativos_usina(usina_id, categorias=None, limit=5):
    """
    Retorna alarmes ativos (status aberta ou em_andamento) de uma usina específica
    
    Args:
        usina_id: ID da usina
        categorias: Lista de categorias para filtrar (ex: ['Hidráulica', 'Automação'])
        limit: Número máximo de alarmes a retornar
    
    Returns:
        Lista de alarmes ativos da usina
    """
    alarmes = [
        ocorrencia for ocorrencia in MOCK_OCORRENCIAS 
        if (ocorrencia.get('usina_id') == usina_id and 
            ocorrencia.get('status') in ['aberta', 'em_andamento'])
    ]
    
    # Filtra por categorias se especificado
    if categorias:
        alarmes = [a for a in alarmes if a.get('categoria') in categorias]
    
    return sorted(alarmes, key=lambda r: r.get("created_at"), reverse=True)[:limit]


def get_timeline_vertedouro(usina_id, limit=5):
    """
    Retorna alarmes relacionados ao vertedouro de uma usina
    Filtra por categorias relacionadas: Hidráulica, Automação
    
    Args:
        usina_id: ID da usina
        limit: Número máximo de alarmes a retornar
    
    Returns:
        Lista de alarmes do vertedouro
    """
    return get_alarmes_ativos_usina(
        usina_id, 
        categorias=['Hidráulica', 'Automação', 'Ambiental'],
        limit=limit
    )
