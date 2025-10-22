f'''
Pode melhorar o prompt abaixo para eu criar a interface em html e css usando o tailwind em uma pagina unica, pode ser usado javascript para melhorar a interação com o usuario. Mas quem vai salvar 
vai ser o backend em python e flask.
Tenho que construrir uma interface para configurar a conexão e as leituras dos dispositivos de uma usina.
A leitura é realizada via VPN a uma API no computador da usina, que disponibiliza um endpoint para ler os dispositivos locais via modbus.

Sendo assim, o objetivo é criar uma interface para que o operador insira novas usinas e dispositivos, com os seguintes requisitos:

Um usina tem apenas 1 IP e 1 porta de comunicação com a API.
A usina pode ter 1 ou mais dispositivos, mas no minimo deve ter 1 dispositivo.
Um dispositivo pode ter apenas 1 IP e 1 porta de comunicação com a API.
Cada dispositivo deve ter 1 IP e 1 porta de comunicação.
Cada dispositivo deve ter suas caracteristicas, sem nome definido.
Cada dispositivo pode ter entradas de leituras, alarmes, temperaturas, comandos ou não ter nada. Mas se preenchidos devem usar os nomes leituras, alarmes, temperaturas, comandos.
Se criadas as entradas, elas podem ter endereços ou não, mas se preenchidos devem ter o tipo[REAL, INT, BOOLEAN], nome e endereço.

Podem ser acrescentadas diversas usinas e dispositivos.

Modelagem das variáveis

variáveis: dict
   nome usina: dict
      ip: str
      port: int
      table: str
      dispositivos: dict  # pode ter 1 ou mais CLPS
         unidade: dict
            conexao: dict
                ip: str
                port: int
            caracteristicas: dict
                potência máxima: float|int   # valor de referencia para a potência da turbina, pode ser um valor inteiro ou decimal
                velocidade máxima: float|int   # valor que representa a caracteristica da turbina, pode ser um valor inteiro ou decimal
            leituras: dict
                REAL: dict
                    nome_da_leitura: int   # 13407, 13408, o endereço modbus para ler o valor real
                INT: dict
                    nome_da_leitura: int   # 13407, 13408, o endereço modbus para ler o valor inteiro
            temperaturas: dict
                REAL: dict
                    nome_da_temperatura: int   # 13407, 13408, o endereço modbus para ler o valor real
                INT: dict
                    nome_da_temperatura: int   # 13407, 13408, o endereço modbus para ler o valor inteiro
            alarmes: dict
                BOOLEAN: dict
                    nome_da_alarma: int   # 24289, 24290, o endereço modbus para ler 0 ou 1
            comandos: dict
                BOOLEAN: dict
                    nome_do_comando: int   # 12529, 12532, o endereço modbus para escrever 0 ou 1
'''

leituras = {

    "CGH APARECIDA": {
        "ip": "100.110.212.125",
        "port": 8010,
        "table": "cgh_aparecida",
        "CLPS": {
            "UG-01": {
                'conexao': {
                    'ip': '192.168.10.2',
                    'port': 502
                }, 
                'caracteristicas': {
                    'potência máxima': 3350,
                    'velocidade máxima': 450
                },
                'leituras': {
                    "INT": { 
                        "Potência Ativa": 13407, 
                    }
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13469,
                        'Enrolamento Fase A alarmes':13989,
                        'Enrolamento Fase A trip':13925,
                        'Enrolamento Fase B value':13471,
                        'Enrolamento Fase B alarmes':13991,
                        'Enrolamento Fase B trip':13927,
                        'Enrolamento Fase C value':13473,
                        'Enrolamento Fase C alarmes':13993,
                        'Enrolamento Fase C trip':13929,
                        'Tiristor 1 value': 13455,
                        'Tiristor 1 alarmes': 13975,
                        'Tiristor 1 trip': 13911,
                        'Tiristor 2 value': 13457,
                        'Tiristor 2 alarmes': 13977,
                        'Tiristor 2 trip': 13913,
                        'Tiristor 3 value': 13459,
                        'Tiristor 3 alarmes': 13979,
                        'Tiristor 3 trip': 13915,
                        'Resistor Crowbar 1 value': 13461,
                        'Resistor Crowbar 1 alarmes': 13983,
                        'Resistor Crowbar 1 trip': 13919,
                        'Resistor Crowbar 2 value': 13491,
                        'Resistor Crowbar 2 alarmes': 13411,
                        'Resistor Crowbar 2 trip': 13497,
                        'Transf. Exitação value': 13463,
                        'Transf. Exitação alarmes': 13983,
                        'Transf. Exitação trip': 13919,
                        'Óleo U.H.R.V. value': 13465,
                        'Óleo U.H.R.V. alarmes': 13985,
                        'Óleo U.H.R.V. trip': 13921,
                        'Óleo U.H.L.M. value': 13467,
                        'Óleo U.H.L.M. alarmes': 13987,
                        'Óleo U.H.L.M. trip': 13923,
                        'Nucleo Estator 1 value': 13475,
                        'Nucleo Estator 1 alarmes': 13995,
                        'Nucleo Estator 1 trip': 13931,
                        'Nucleo Estator 2 value': 13477,
                        'Nucleo Estator 2 alarmes': 13997,
                        'Nucleo Estator 2 trip': 13933,
                        'Nucleo Estator 3 value': 13479,
                        'Nucleo Estator 3 alarmes': 13999,
                        'Nucleo Estator 3 trip': 13935,
                        'Manc. Casq. Rad. Guia value': 13481,
                        'Manc. Casq. Rad. Guia alarmes': 14001,
                        'Manc. Casq. Rad. Guia trip': 13937,
                        'Mancal Comb. Casq value': 13483,
                        'Mancal Comb. Casq alarmes': 14003,
                        'Mancal Comb. Casq trip': 13939,
                        'Mancal Comb. Esc. value': 13485,
                        'Mancal Comb. Esc. alarmes': 14005,
                        'Mancal Comb. Esc. trip': 13941,
                        'Mancal Comb. Contra Esc. value': 13487,
                        'Mancal Comb. Contra Esc. alarmes': 14007,
                        'Mancal Comb. Contra Esc. trip': 13943,
                        'Mancal Guia Casq. Turb. value': 13489,
                        'Mancal Guia Casq. Turb. alarmes': 14009,
                        'Mancal Guia Casq. Turb. trip': 13945, 
                    }
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289, 
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290
                    },
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12850,
                        "CalaSirene SuperSEP": 12852,
                        "Reset local": 12849
                    },
                },
                "alarmes_reset_automatico": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                    }
                },
            },
        }
    },
    "CGH FAE": {
        "ip": "100.106.33.66",
        "port": 8010,
        "table": "cgh_fae",
        "CLPS": {
            "UG-01": {
                'conexao': {
                    'ip': '192.168.10.2',
                    'port': 502
                }, 
                'caracteristicas': {
                    'potência máxima': 1350,
                    'velocidade máxima': 415
                },
                'leituras': {
                    "REAL": {
                        "Potência Ativa": 13407
                    },
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13455,
                        'Enrolamento Fase A alarmes':13975,
                        'Enrolamento Fase A trip':13911,
                        'Enrolamento Fase B value':13457,
                        'Enrolamento Fase B alarmes':13977,
                        'Enrolamento Fase B trip':13913,
                        'Enrolamento Fase C value':13459,
                        'Enrolamento Fase C alarmes':13979,
                        'Enrolamento Fase C trip':13915,
                        'Nucleo do estator value': 13461,
                        'Nucleo do estator alarmes': 13981,
                        'Nucleo do estator trip': 13917,
                        'Mancal Guia value': 13463,
                        'Mancal Guia alarmes': 13983,
                        'Mancal Guia trip': 13919,
                        'Mancal Combinado value': 13465,
                        'Mancal Combinado alarmes': 13985,
                        'Mancal Combinado trip': 13921,
                        'Mancal Escora value': 13467,
                        'Mancal Escora alarmes': 13987,
                        'Mancal Escora trip': 13923,
                        'Óleo U.H.R.V. value': 13469,
                        'Óleo U.H.R.V. alarmes': 13989,
                        'Óleo U.H.R.V. trip': 13925,
                        'Óleo U.H.L.M. value': 13471,
                        'Óleo U.H.L.M. alarmes': 13991,
                        'Óleo U.H.L.M. trip': 13927,
                        # 'ENGEXC value': 13475,
                        # 'ENGEXC alarmes': 13997,
                        # 'ENGEXC trip': 13933,
                        # 'CSS-U1 value': 13475,
                        # 'CSS-U1 alarmes': 13995,
                        # 'CSS-U1 trip': 13931,
                    },
                },
                "vibrações": {
                    "REAL": {
                        'Vib. Mancal Guia X value': 13463,
                        'Vib. Mancal Guia X alarmes': 13983,
                        'Vib. Mancal Guia X trip': 13919,
                        'Vib. Mancal Guia Y value': 13465,
                        'Vib. Mancal Guia Y alarmes': 13985,
                        'Vib. Mancal Guia Y trip': 13921,
                        'Vib. Mancal Comb. X value': 13467,
                        'Vib. Mancal Comb. X alarmes': 13987,
                        'Vib. Mancal Comb. X trip': 13923,
                        'Vib. Mancal Comb. Y value': 13469,
                        'Vib. Mancal Comb. Y alarmes': 13989,
                        'Vib. Mancal Comb. Y trip': 13925,
                        'Vib. Mancal Comb. Z value': 13471,
                        'Vib. Mancal Comb. Z alarmes': 13991,
                        'Vib. Mancal Comb. Z trip': 13927,
                        
                    }
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            "UG-02": {
                'conexao': {
                    'ip': '192.168.10.3',
                    'port': 502
                },
                'caracteristicas': {
                    'potência máxima': 650,
                    'velocidade máxima': 800,
                },
                'leituras': {
                    "REAL": {
                        "Potência Ativa": 13407, 
                        # "Potência Ativa Acumulada": 13541, 
                        # "Turbina Velocidade": 13321
                    },
                    # "INT": {},
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13455,
                        'Enrolamento Fase A alarmes':13975,
                        'Enrolamento Fase A trip':13911,
                        'Enrolamento Fase B value':13457,
                        'Enrolamento Fase B alarmes':13977,
                        'Enrolamento Fase B trip':13913,
                        'Enrolamento Fase C value':13459,
                        'Enrolamento Fase C alarmes':13979,
                        'Enrolamento Fase C trip':13915,
                        'Nucleo do estator value': 13461,
                        'Nucleo do estator alarmes': 13981,
                        'Nucleo do estator trip': 13917,
                        'Mancal Guia value': 13463,
                        'Mancal Guia alarmes': 13983,
                        'Mancal Guia trip': 13919,
                        'Mancal Combinado value': 13465,
                        'Mancal Combinado alarmes': 13985,
                        'Mancal Combinado trip': 13921,
                        'Mancal Escora value': 13467,
                        'Mancal Escora alarmes': 13987,
                        'Mancal Escora trip': 13923,
                        'Óleo U.H.R.V. value': 13469,
                        'Óleo U.H.R.V. alarmes': 13989,
                        'Óleo U.H.R.V. trip': 13925,
                        'Óleo U.H.L.M. value': 13471,
                        'Óleo U.H.L.M. alarmes': 13991,
                        'Óleo U.H.L.M. trip': 13927,
                        'ENGEXC value': 13475,
                        'ENGEXC alarmes': 13997,
                        'ENGEXC trip': 13933,
                        'CSS-U1 value': 13475,
                        'CSS-U1 alarmes': 13995,
                        'CSS-U1 trip': 13931,
                    },
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
        },
    },
    "PCH PEDRAS": {
        "ip": "100.93.237.40",
        "port": 8010,
        "table": "pch_pedras",
        "CLPS": {
            "UG-01": {
                'conexao': {
                    'ip': '192.168.10.2',
                    'port': 502
                }, 
                'caracteristicas': {
                    'potência máxima': 2800,
                    'velocidade máxima': 450,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13459,
                        'Enrolamento Fase A alarmes':13979,
                        'Enrolamento Fase A trip':13915,
                        'Enrolamento Fase B value':13461,
                        'Enrolamento Fase B alarmes':13981,
                        'Enrolamento Fase B trip':13917,
                        'Enrolamento Fase C value':13463,
                        'Enrolamento Fase C alarmes':13983,
                        'Enrolamento Fase C trip':13919,
                        'G Mancal L.A. Guia value':13465,
                        'G Mancal L.A. Guia alarmes': 13985,
                        'G Mancal L.A. Guia trip': 13921,
                        'G Mancal L.N.A. Guia value': 13469,
                        'G Mancal L.N.A. Guia alarmes': 13989,
                        'G Mancal L.N.A. Guia trip': 13925,
                        'G Mancal L.N.A. Escora value': 13467,
                        'G Mancal L.N.A. Escora alarmes':13987,
                        'G Mancal L.N.A. Escora trip': 13923,
                        'T Bucha Radial 01 value': 13457,
                        'T Bucha Radial 01 alarmes': 13977,
                        'T Bucha Radial 01 trip': 13913,
                        'T Bucha Radial 02 value': 13475,
                        'T Bucha Radial 02 alarmes': 13995,
                        'T Bucha Radial 02 trip': 13931,
                        'T Gaxeteiro 01 value':13455,
                        'T Gaxeteiro 01 alarmes': 13975,
                        'T Gaxeteiro 01 trip': 13911,
                        'T Gaxeteiro 02 value':13473,
                        'T Gaxeteiro 02 alarmes': 13993,
                        'T Gaxeteiro 02 trip': 13929,
                        'T Gaxeteiro 03 value': 13471,
                        'T Gaxeteiro 03 alarmes': 13991,
                        'T Gaxeteiro 03 trip': 13927,
                        'Óleo U.H.L.M. value': 13481,
                        'Óleo U.H.L.M. alarmes':14001,
                        'Óleo U.H.L.M. trip':13937,
                        'Óleo U.H.R.V. value':13479,
                        'Óleo U.H.R.V. alarmes':13999,
                        'Óleo U.H.R.V. trip':13935,
                    },
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            "UG-02": {
                'conexao': {'ip': '192.168.10.3', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 2800,
                    'velocidade máxima': 450,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13459,
                        'Enrolamento Fase A alarmes':13979,
                        'Enrolamento Fase A trip':13915,
                        'Enrolamento Fase B value':13461,
                        'Enrolamento Fase B alarmes':13981,
                        'Enrolamento Fase B trip':13917,
                        'Enrolamento Fase C value':13463,
                        'Enrolamento Fase C alarmes':13983,
                        'Enrolamento Fase C trip':13919,
                        'G Mancal L.A. Guia value':13465,
                        'G Mancal L.A. Guia alarmes': 13985,
                        'G Mancal L.A. Guia trip': 13921,
                        'G Mancal L.N.A. Guia value': 13469,
                        'G Mancal L.N.A. Guia alarmes': 13989,
                        'G Mancal L.N.A. Guia trip': 13925,
                        'G Mancal L.N.A. Escora value': 13467,
                        'G Mancal L.N.A. Escora alarmes':13987,
                        'G Mancal L.N.A. Escora trip': 13923,
                        'T Bucha Radial 01 value': 13457,
                        'T Bucha Radial 01 alarmes': 13977,
                        'T Bucha Radial 01 trip': 13913,
                        'T Bucha Radial 02 value': 13475,
                        'T Bucha Radial 02 alarmes': 13995,
                        'T Bucha Radial 02 trip': 13931,
                        'T Gaxeteiro 01 value':13455,
                        'T Gaxeteiro 01 alarmes': 13975,
                        'T Gaxeteiro 01 trip': 13911,
                        'T Gaxeteiro 02 value':13473,
                        'T Gaxeteiro 02 alarmes': 13993,
                        'T Gaxeteiro 02 trip': 13929,
                        'T Gaxeteiro 03 value': 13471,
                        'T Gaxeteiro 03 alarmes': 13991,
                        'T Gaxeteiro 03 trip': 13927,
                        'Óleo U.H.L.M. value': 13481,
                        'Óleo U.H.L.M. alarmes':14001,
                        'Óleo U.H.L.M. trip':13937,
                        'Óleo U.H.R.V. value':13479,
                        'Óleo U.H.R.V. alarmes':13999,
                        'Óleo U.H.R.V. trip':13935,
                    },
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
        }
    },
    "CGH PICADAS ALTAS": {
        "ip": "100.79.241.13",
        "port": 8010,
        "table": "cgh_picadas_altas",
        "CLPS": {
            "UG-01": {
                'conexao': {'ip': '192.168.10.2', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 300,
                    'velocidade máxima': 450,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13455,
                        'Enrolamento Fase A alarmes':13975,
                        'Enrolamento Fase A trip':13911,
                        'Enrolamento Fase B value':13457,
                        'Enrolamento Fase B alarmes':13977,
                        'Enrolamento Fase B trip':13913,
                        'Enrolamento Fase C value':13459,
                        'Enrolamento Fase C alarmes':13979,
                        'Enrolamento Fase C trip':13915,
                        'Nucleo do estator value':13461,
                        'Nucleo do estator alarmes':13981,
                        'Nucleo do estator trip':13917,
                        'CS-U2 value':13475,
                        'CS-U2 alarmes': 13995,
                        'CS-U2 trip': 13931,
                        'Manc. Comb. Rad. L.A. value':13463,
                        'Manc. Comb. Rad. L.A. alarmes': 13983,
                        'Manc. Comb. Rad. L.A. trip': 13919,
                        'Manc. Comb. Esc. L.A. value': 13465,
                        'Manc. Comb. Esc. L.A. alarmes': 13985,
                        'Manc. Comb. Esc. L.A. trip': 13921,
                        'Manc. Cont. Esc. L.A. value': 13467,
                        'Manc. Cont. Esc. L.A. alarmes': 13987,
                        'Manc. Cont. Esc. L.A. trip': 13923,
                        'Mancal Guia L.N.A. value':13469,
                        'Mancal Guia L.N.A. alarmes': 13989,
                        'Mancal Guia L.N.A. trip': 13925,
                        'Óleo U.H.L.M. value':13473,
                        'Óleo U.H.L.M. alarmes': 13993,
                        'Óleo U.H.L.M. trip': 13929,
                    },
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            "UG-02": {
                'conexao': {'ip': '192.168.10.3', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 700,
                    'velocidade máxima': 450,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13455,
                        'Enrolamento Fase A alarmes':13975,
                        'Enrolamento Fase A trip':13911,
                        'Enrolamento Fase B value':13457,
                        'Enrolamento Fase B alarmes':13977,
                        'Enrolamento Fase B trip':13913,
                        'Enrolamento Fase C value':13459,
                        'Enrolamento Fase C alarmes':13979,
                        'Enrolamento Fase C trip':13915,
                        'Nucleo do estator value':13461,
                        'Nucleo do estator alarmes':13981,
                        'Nucleo do estator trip':13917,
                        'CS-U2 value':13475,
                        'CS-U2 alarmes': 13995,
                        'CS-U2 trip': 13931,
                        'Manc. Comb. Rad. L.A. value':13463,
                        'Manc. Comb. Rad. L.A. alarmes': 13983,
                        'Manc. Comb. Rad. L.A. trip': 13919,
                        'Manc. Comb. Esc. L.A. value': 13465,
                        'Manc. Comb. Esc. L.A. alarmes': 13985,
                        'Manc. Comb. Esc. L.A. trip': 13921,
                        'Manc. Cont. Esc. L.A. value': 13467,
                        'Manc. Cont. Esc. L.A. alarmes': 13987,
                        'Manc. Cont. Esc. L.A. trip': 13923,
                        'Mancal Guia L.N.A. value':13469,
                        'Mancal Guia L.N.A. alarmes': 13989,
                        'Mancal Guia L.N.A. trip': 13925,
                        'Óleo U.H.L.M. value':13473,
                        'Óleo U.H.L.M. alarmes': 13993,
                        'Óleo U.H.L.M. trip': 13929,
                    },
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
        }
    },
    "CGH HOPPEN": {
        "ip": "100.73.37.105",
        "port": 8010,
        "table": "cgh_hoppen",
        "CLPS": {
            "UG-01": {
                'conexao': {'ip': '192.168.10.2', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 1300,
                    'velocidade máxima': 415,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13455,
                        'Enrolamento Fase A alarmes':13975,
                        'Enrolamento Fase A trip':13911,
                        'Enrolamento Fase B value':13457,
                        'Enrolamento Fase B alarmes':13977,
                        'Enrolamento Fase B trip':13913,
                        'Enrolamento Fase C value':13459,
                        'Enrolamento Fase C alarmes':13979,
                        'Enrolamento Fase C trip':13915,
                        'Nucleo do estator value':13461,
                        'Nucleo do estator alarmes':13981,
                        'Nucleo do estator trip':13917,
                        'Vedação do eixo LNA value':13463,
                        'Vedação do eixo LNA alarmes':13983,
                        'Vedação do eixo LNA trip':13919,
                        'Vedação do eixo LA value':13465,
                        'Vedação do eixo LA alarmes':13985,
                        'Vedação do eixo LA trip':13921,
                        'Mancal Escora Combinado value':13467,
                        'Mancal Escora Combinado alarmes':13987,
                        'Mancal Escora Combinado trip':13923,
                        'Mancal Radial Combinado value':13469,
                        'Mancal Radial Combinado alarmes':13989,
                        'Mancal Radial Combinado trip':13925,
                        'Cont. Esc. Manc. Comb. value': 13471,
                        'Cont. Esc. Manc. Comb. alarmes': 13991,
                        'Cont. Esc. Manc. Comb. trip': 13927,
                        'Mancal Radial Guia value': 13473,
                        'Mancal Radial Guia alarmes': 13993,
                        'Mancal Radial Guia trip': 13929,
                        'Mancal Rad. Comb. L.A. value': 13475,
                        'Mancal Rad. Comb. L.A. alarmes': 13995,
                        'Mancal Rad. Comb. L.A. trip': 13931,
                        'Mancal Rad. Comb. L.N.A. value': 13477,
                        'Mancal Rad. Comb. L.N.A. alarmes': 13997,
                        'Mancal Rad. Comb. L.N.A. trip': 13933,
                        'Óleo U.H.R.V. value': 13479,
                        'Óleo U.H.R.V. alarmes': 13999,
                        'Óleo U.H.R.V. trip': 13935,
                        'Óleo U.H.L.M. value': 13481,
                        'Óleo U.H.L.M. alarmes': 14001,
                        'Óleo U.H.L.M. trip': 13937,
                        'CS-01 value': 13483,
                        'CS-01 alarmes': 14003,
                        'CS-01 trip': 13939,
                    },
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            "UG-02": {
                'conexao': {'ip': '192.168.10.3', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 1300,
                    'velocidade máxima': 415,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas": {
                    "REAL": {
                        'Enrolamento Fase A value':13455,
                        'Enrolamento Fase A alarmes':13975,
                        'Enrolamento Fase A trip':13911,
                        'Enrolamento Fase B value':13457,
                        'Enrolamento Fase B alarmes':13977,
                        'Enrolamento Fase B trip':13913,
                        'Enrolamento Fase C value':13459,
                        'Enrolamento Fase C alarmes':13979,
                        'Enrolamento Fase C trip':13915,
                        'Nucleo do estator value':13461,
                        'Nucleo do estator alarmes':13981,
                        'Nucleo do estator trip':13917,
                        'Vedação do eixo LNA value':13463,
                        'Vedação do eixo LNA alarmes':13983,
                        'Vedação do eixo LNA trip':13919,
                        'Vedação do eixo LA value':13465,
                        'Vedação do eixo LA alarmes':13985,
                        'Vedação do eixo LA trip':13921,
                        'Mancal Escora Combinado value':13467,
                        'Mancal Escora Combinado alarmes':13987,
                        'Mancal Escora Combinado trip':13923,
                        'Mancal Radial Combinado value':13469,
                        'Mancal Radial Combinado alarmes':13989,
                        'Mancal Radial Combinado trip':13925,
                        'Cont. Esc. Manc. Comb. value': 13471,
                        'Cont. Esc. Manc. Comb. alarmes': 13991,
                        'Cont. Esc. Manc. Comb. trip': 13927,
                        'Mancal Radial Guia value': 13473,
                        'Mancal Radial Guia alarmes': 13993,
                        'Mancal Radial Guia trip': 13929,
                        'Mancal Rad. Comb. L.A. value': 13475,
                        'Mancal Rad. Comb. L.A. alarmes': 13995,
                        'Mancal Rad. Comb. L.A. trip': 13931,
                        'Mancal Rad. Comb. L.N.A. value': 13477,
                        'Mancal Rad. Comb. L.N.A. alarmes': 13997,
                        'Mancal Rad. Comb. L.N.A. trip': 13933,
                        'Óleo U.H.R.V. value': 13479,
                        'Óleo U.H.R.V. alarmes': 13999,
                        'Óleo U.H.R.V. trip': 13935,
                        'Óleo U.H.L.M. value': 13481,
                        'Óleo U.H.L.M. alarmes': 14001,
                        'Óleo U.H.L.M. trip': 13937,
                        'CS-01 value': 13483,
                        'CS-01 alarmes': 14003,
                        'CS-01 trip': 13939,
                    },
                },
                "alarmes": {
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos": {
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
        }
    }
}