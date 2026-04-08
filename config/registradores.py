# Endereços Modbus confirmados da TELA DO SCADA (MdbMeter offset 2560)
# Nome | Endereço | Tipo | Offset | Conversor
REGISTERS = {
    # --- Medidas Gerador --- 9
    "potencia_ativa":             [2588, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[14]
    "potencia_reativa":           [2590, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[15]
    "fator_potencia":             [2594, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[17]
    "horimetro_gerador":          [2648, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[44]
    "energia_acumulada":          [2652, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[46] - Total Geração
    "tensao":                     [2574, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[7]
    "corrente":                   [2582, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[11]
    "freq":                       [2560, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[0]
    "horimetro":                  [2648, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

    # --- Excitação --- 3
    "excitacao_corrente":   [2602, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[21] - If_
    "excitacao_disparo":    [19195, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[54]
    # "temp_ponte_tiristores":[2642, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # MdbMeter[41] - ExcTemp
    "temp_ponte_tiristores":      [2642, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

    # --- Unidades Hidráulicas (UHRV / UHLM) --- 4
    "pressao_oleo_uhrv":         [19135, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[24]
    "pressao_oleo_uhlm":         [19117, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[15]
    "temp_oleo_uhrv":            [19619, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    "temp_oleo_uhlm":            [19623, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

    # --- Níveis --- 3
    "nivel_camara_carga":   [21787, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # QCC - montante
    "nivel_barragem":       [21793, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # QCC - barragem
    "nivel_jusante":        [19187, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[50]

    # # --- Temperaturas Gerador --- 4
    "temp_ger_fase_r":            [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~65°C (ajustar depois)
    "temp_ger_fase_s":            [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    "temp_ger_fase_t":            [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    "temp_ger_nucleo":            [2632, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

    # # --- Temperaturas Mancais Gerador --- 4
    "temp_mancal_comb_escora":    [2632, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~73°C (possível escora)
    "temp_mancal_comb_casq":      [2646, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~58°C
    "temp_mancal_comb_contra":    [2604, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~60°C
    "temp_mancal_guia_ger":       [2624, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~60°C

    # # --- Temperaturas Mancais Turbina --- 2
    "temp_mancal_guia_turb_1":    [19131, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~49°C (melhor match)
    "temp_mancal_guia_turb_2":    [19131, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # mesmo bloco

    # # --- Temperaturas Gerador --- 4
    # "temp_ger_fase_r":      [19611, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    # "temp_ger_fase_s":      [19613, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    # "temp_ger_fase_t":      [19615, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    # "temp_ger_nucleo":      [19617, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    
    # # --- Temperaturas Mancais Gerador --- 4
    # "temp_mancal_comb_escora": [2620, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    # "temp_mancal_comb_casq":   [2622, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    # "temp_mancal_comb_contra": [2624, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    # "temp_mancal_guia_ger":    [2626, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

    # # --- Temperaturas Mancais Turbina --- 2
    # "temp_mancal_guia_turb_1": [2628, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    # "temp_mancal_guia_turb_2": [2630, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

    # --- Vibração Gerador --- 5
    "vib_ger_mancal_comb_x":   [19171, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[42]
    "vib_ger_mancal_comb_y":   [19175, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[44]
    "vib_ger_mancal_comb_z":   [19179, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[46]
    "vib_ger_mancal_guia_x":   [19163, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[38]
    "vib_ger_mancal_guia_y":   [19167, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[40]

    # --- Vibração Turbina --- 2
    "vib_turb_mancal_guia_x":  [19149, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[31]
    "vib_turb_mancal_guia_y":  [19153, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[33]

    # --- Turbina / Conduto --- 4
    "rotacao":              [2628, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MdbMeter[34]
    "pos_distribuidor":     [2632, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MdbMeter[36]
    "pos_rotor":            [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MdbMeter[38]
    "pressao_conduto":      [19145, "INPUT_REAL", {"offset": 0, "converter": "word_order"}], # MDB_Medidas[29]

    # total 40 variaveis
}

REGISTERS_ATUAL = {
    "UG01": {
        "10.200.20.11": {
            # --- Medidas Gerador --- 9
            "potencia_ativa":             [2588, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "potencia_reativa":           [2590, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "fator_potencia":             [2594, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "horimetro_gerador":          [2648, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "energia_acumulada":          [2652, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "tensao":                     [2574, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "corrente":                   [2582, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "freq":                       [2560, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "tempo_geracao":              [2648, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

            # --- Excitação --- 3
            "excitacao_corrente":         [2602, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "excitacao_disparo":          [19195, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "temp_ponte_tiristores":      [2642, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

            # --- Temperaturas Gerador / Mancais --- 6
            "temp_mancal_guia_turb_1":    [19131, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~49°C (melhor match)
            "temp_mancal_guia_turb_2":    [19131, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # mesmo bloco

            "temp_mancal_comb_escora":    [2632, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~73°C (possível escora)
            "temp_mancal_comb_casq":      [2646, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~58°C
            "temp_mancal_comb_contra":    [2604, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~60°C

            "temp_mancal_guia_ger":       [2624, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~60°C

            # --- Temperaturas Gerador --- 4
            "temp_ger_fase_r":            [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # ~65°C (ajustar depois)
            "temp_ger_fase_s":            [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "temp_ger_fase_t":            [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
            "temp_ger_nucleo":            [2632, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

            # total 22
        },

        "10.200.20.61": {
            # --- Níveis (PSA - melhores matches reais) --- 3
            "nivel_camara_carga": [19381, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # 390.46
            "nivel_barragem":     [19393, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # 390.45
            "nivel_jusante":      [19171, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # faixa válida
        },

        "10.200.20.14": {
            # --- Backup / redundância --- 1
            "nivel_barragem_alt": [19102, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        }

        # total 27
    }
}


# REGISTERS_ATUAL = {
#     "UG01": {
#         "10.200.20.11": {

#             # --- Medidas Gerador --- 9
#             "potencia_ativa":     [2588, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "potencia_reativa":   [2590, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "fator_potencia":     [2594, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "horimetro_gerador":  [2648, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "energia_acumulada":  [2652, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "tensao":             [2574, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "corrente":           [2582, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "freq":               [2560, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "tempo_geracao":      [2648, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

#             # --- Excitação --- 3
#             "excitacao_corrente":    [2602, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "excitacao_disparo":     [19195, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_ponte_tiristores": [2642, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

#             # --- Unidades Hidráulicas --- 4
#             "pressao_oleo_uhrv":     [19130, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "pressao_oleo_uhlm":     [19117, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_oleo_uhrv":        [19131, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_oleo_uhlm":        [19194, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

#             # --- Turbina / Conduto --- 4
#             "rotacao":           [2604, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "pos_distribuidor":  [2624, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "pos_rotor":         [2646, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "pressao_conduto":   [2650, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

#             # --- Temperaturas Gerador --- 4
#             "temp_ger_fase_r":   [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_ger_fase_s":   [2638, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_ger_fase_t":   [2640, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_ger_nucleo":   [2632, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

#             # --- Temperaturas Mancais Gerador --- 4
#             "temp_mancal_comb_escora": [2632, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_mancal_comb_casq":   [2646, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_mancal_comb_contra": [2604, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_mancal_guia_ger":    [2624, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

#             # --- Temperaturas Mancais Turbina --- 2
#             "temp_mancal_guia_turb_1": [19131, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "temp_mancal_guia_turb_2": [19131, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

#             # --- Vibração Gerador --- 5
#             "vib_ger_mancal_comb_x": [19177, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "vib_ger_mancal_comb_y": [19179, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "vib_ger_mancal_comb_z": [19181, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "vib_ger_mancal_guia_x": [19183, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "vib_ger_mancal_guia_y": [19185, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

#             # --- Vibração Turbina --- 2
#             "vib_turb_mancal_guia_x": [19149, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "vib_turb_mancal_guia_y": [19151, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#         },

#         "10.200.20.61": {
#             # --- Níveis --- 3
#             "nivel_camara_carga": [19381, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "nivel_barragem":     [19393, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#             "nivel_jusante":      [19171, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#         },

#         "10.200.20.14": {
#             # --- Backup --- 1
#             "nivel_barragem_alt": [19102, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
#         }
#     }
# }

# Melhores candidatos encontrados na investigacao.
# Mantidos separados do REGISTERS principal porque varios desses pontos
# estao em CLPs remotos (PSA/QCC) e o fluxo atual da UG01 ainda le tudo
# usando o IP da propria unidade geradora.
BEST_REMOTE_CANDIDATES = {
    "nivel_camara_carga": {
        "best": {"source": "PSA", "ip": "10.200.20.61", "address": 19381, "type": "INPUT_REAL"},
        "alternatives": [
            {"source": "PSA", "ip": "10.200.20.61", "address": 19385, "type": "INPUT_REAL"},
            {"source": "QCC-UG01", "ip": "10.200.20.14", "address": 19103, "type": "INPUT_REAL"},
        ],
    },
    "nivel_barragem": {
        "best": {"source": "PSA", "ip": "10.200.20.61", "address": 19385, "type": "INPUT_REAL"},
        "alternatives": [
            {"source": "QCC-UG01", "ip": "10.200.20.14", "address": 19103, "type": "INPUT_REAL"},
            {"source": "PSA", "ip": "10.200.20.61", "address": 19381, "type": "INPUT_REAL"},
        ],
    },
    "nivel_jusante": {
        "best": {"source": "PSA", "ip": "10.200.20.61", "address": 19171, "type": "INPUT_REAL"},
        "alternatives": [
            {"source": "PSA", "ip": "10.200.20.61", "address": 19271, "type": "INPUT_REAL"},
            {"source": "PSA", "ip": "10.200.20.61", "address": 19169, "type": "INPUT_REAL"},
        ],
    },
    "temperaturas_ug01": {
        "candidates": [
            {"address": 2604, "type": "INPUT_REAL", "note": "faixa ~60 C"},
            {"address": 2624, "type": "INPUT_REAL", "note": "faixa ~60 C"},
            {"address": 2646, "type": "INPUT_REAL", "note": "faixa ~55 C"},
            {"address": 19130, "type": "INPUT_REAL", "note": "faixa ~47 C"},
            {"address": 19194, "type": "INPUT_REAL", "note": "faixa ~56 C"},
            {"address": 2657, "type": "INPUT_REAL", "note": "faixa ~48 C"},
        ],
    },
}

# Versao compacta so com os enderecos que hoje fazem mais sentido para conferencia manual.
BEST_CANDIDATE_ADDRESSES = {
    "PSA": {
        "nivel_camara_carga": 19381,
        "nivel_barragem": 19385,
        "nivel_jusante": 19171,
    },
    "QCC-UG01": {
        "nivel_barragem_alt": 19103,
    },
    "UG01": {
        "temp_cand_1": 2604,
        "temp_cand_2": 2624,
        "temp_cand_3": 2646,
        "temp_cand_4": 19130,
        "temp_cand_5": 19194,
        "temp_cand_6": 2657,
    },
}

# CLPs da PCH Pira
CLPS = {
    "UG01": "10.200.20.11",
    "UG02": "10.200.20.21",
    "UG03": "10.200.20.31",
    "UG04": "10.200.20.41",
    "MC01": "10.200.20.51",
}
# Variaveis de validação, são maximos e minimos que as variaveis podem atingir
UGS = {
    "UG01": {
        # --- Medidas Gerador ---
        "potencia_ativa":       [0.9, 8152.1],
        "potencia_reativa":     [-700.6, 464.4],
        "fator_potencia":       [-1.1, 1.9],
        "horimetro_gerador":    [1382.5, 1689.7],
        "energia_acumulada":    [7223.7, 8829.0],
        "tensao":               [6373.8, 7790.2],
        "corrente":             [1.0, 667.7],
        "freq":                 [54.0, 66.0],

        # --- Excitação ---
        "excitacao_corrente":   [1.09, 11.11],
        "excitacao_disparo":    [50.0, 110.0],
        "temp_ponte_tiristores":[45.18, 55.22],

        # --- Unidades Hidráulicas ---
        "pressao_oleo_uhrv":    [114.48, 139.92],
        "pressao_oleo_uhlm":    [119.0, 130.0],
        "temp_oleo_uhrv":       [1.0, 100.0],
        "temp_oleo_uhlm":       [1.0, 100.0],

        # --- Turbina / Conduto ---
        "rotacao":              [202.5, 247.5],
        "pos_distribuidor":     [0.42, 100.0],
        "pos_rotor":            [59.13, 72.27],
        "pressao_conduto":      [1.70, 2.08],

        # --- Níveis ---
        "nivel_camara_carga":   [351.20, 429.24],
        "nivel_barragem":       [351.48, 429.58],
        "nivel_jusante":        [370.0, 382.0],

        # --- Temperaturas Gerador ---
        "temp_ger_fase_r":      [1.0, 100.0],
        "temp_ger_fase_s":      [1.0, 100.0],
        "temp_ger_fase_t":      [1.0, 100.0],
        "temp_ger_nucleo":      [1.0, 100.0],

        # --- Temperaturas Mancais Gerador ---
        "temp_mancal_comb_escora": [1.0, 100.0],
        "temp_mancal_comb_casq":   [1.0, 100.0],
        "temp_mancal_comb_contra": [1.0, 100.0],
        "temp_mancal_guia_ger":    [1.0, 100.0],

        # --- Temperaturas Mancais Turbina ---
        "temp_mancal_guia_turb_1": [1.0, 100.0],
        "temp_mancal_guia_turb_2": [1.0, 100.0],

        # --- Vibração Gerador --- 5
        "vib_ger_mancal_comb_x":   [0.01, 0.60],   # mm/s | RANGE AMPLIADO - lendo 0.33~0.36 | atual: 0.3 mm/s
        "vib_ger_mancal_comb_y":   [0.01, 0.50],   # mm/s | RANGE AMPLIADO - lendo 0.27~0.28 | atual: 0.3 mm/s
        "vib_ger_mancal_comb_z":   [0.01, 0.66],   # mm/s | OK end.19179 | atual: 0.6 mm/s
        "vib_ger_mancal_guia_x":   [0.01, 0.35],   # mm/s | RANGE AMPLIADO - lendo 0.14~0.15 | atual: 0.2 mm/s
        "vib_ger_mancal_guia_y":   [0.01, 0.25],   # mm/s | RANGE AMPLIADO - lendo 0.13~0.14 | atual: 0.1 mm/s

        # --- Vibração Turbina --- 2
        "vib_turb_mancal_guia_x":  [0.01, 0.93],   # mm/s | OK end.19149 | atual: 0.3 mm/s
        "vib_turb_mancal_guia_y":  [0.01, 0.90],   # mm/s | RANGE AMPLIADO - lendo 0.35~0.41 | atual: 0.4 mm/s
    },
}
'''
Novos valores:

"excitacao_corrente":   [26890, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
"temp_oleo_uhrv":            [26100, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
"nivel_jusante":        [19187, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
"temp_ger_fase_r":      [2612, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
"temp_mancal_comb_escora": [2620, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
"temp_mancal_guia_turb_1": [2628, "INPUT_REAL", {"offset": 0, "converter": "word_order"}]
"vib_ger_mancal_comb_x":   [19171, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
"rotacao":              [2628, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

'''
'''
Com base na imagem em anexo, preciso que você implemente valores para as variáveis abaixo, esses valores são o minimo e o maximo que cada variável pode assumir,
a imagem é da UG01 e muda constantemente, então o intervalo deve ficar +/- 20% do valor atual. Se faltar alguma, deixe como está, não acrescente e nem retire variaveis do dict

# Variaveis de validação, são maximos e minimos que as variaveis podem atingir
UGS = {
    "UG01": {
        # --- Medidas Gerador ---
        "potencia_ativa":       [6669.9, 8152.1],
        "potencia_reativa":     [-600.6, 464.4],
        "fator_potencia":       [-1.1, 1.9],
        "horimetro_gerador":    [1382.5, 1689.7],
        "energia_acumulada":    [7223.7, 8829.0],
        "tensao":               [6373.8, 7790.2],
        "corrente":             [546.3, 667.7],
        "freq":                 [54.0, 66.0],

        # --- Excitação ---
        "excitacao_corrente":   [9.09, 11.11],
        "excitacao_disparo":    [90.0, 110.0],
        "temp_ponte_tiristores":[45.18, 55.22],

        # --- Unidades Hidráulicas ---
        "pressao_oleo_uhrv":    [114.48, 139.92],
        "pressao_oleo_uhlm":    [119.0, 130.0],
        "temp_oleo_uhrv":       [31.5, 38.5],
        "temp_oleo_uhlm":       [44.1, 53.9],

        # --- Turbina / Conduto ---
        "rotacao":              [202.5, 247.5],
        "pos_distribuidor":     [0.42, 100.0],
        "pos_rotor":            [59.13, 72.27],
        "pressao_conduto":      [1.70, 2.08],

        # --- Níveis ---
        "nivel_camara_carga":   [351.20, 429.24],
        "nivel_barragem":       [351.48, 429.58],
        "nivel_jusante":        [370.0, 382.0],

        # --- Temperaturas Gerador ---
        "temp_ger_fase_r":      [91.8, 112.2],
        "temp_ger_fase_s":      [90.0, 110.0],
        "temp_ger_fase_t":      [90.0, 110.0],
        "temp_ger_nucleo":      [66.6, 81.4],

        # --- Temperaturas Mancais Gerador ---
        "temp_mancal_comb_escora": [59.4, 72.6],
        "temp_mancal_comb_casq":   [52.2, 63.8],
        "temp_mancal_comb_contra": [32.4, 39.6],
        "temp_mancal_guia_ger":    [45.0, 55.0],

        # --- Temperaturas Mancais Turbina ---
        "temp_mancal_guia_turb_1": [44.1, 53.9],
        "temp_mancal_guia_turb_2": [44.1, 53.9],

        # --- Vibração Gerador --- 5
        "vib_ger_mancal_comb_x":   [0.05, 0.60],   # mm/s | RANGE AMPLIADO - lendo 0.33~0.36 | atual: 0.3 mm/s
        "vib_ger_mancal_comb_y":   [0.05, 0.50],   # mm/s | RANGE AMPLIADO - lendo 0.27~0.28 | atual: 0.3 mm/s
        "vib_ger_mancal_comb_z":   [0.05, 0.66],   # mm/s | OK end.19179 | atual: 0.6 mm/s
        "vib_ger_mancal_guia_x":   [0.05, 0.35],   # mm/s | RANGE AMPLIADO - lendo 0.14~0.15 | atual: 0.2 mm/s
        "vib_ger_mancal_guia_y":   [0.05, 0.25],   # mm/s | RANGE AMPLIADO - lendo 0.13~0.14 | atual: 0.1 mm/s

        # --- Vibração Turbina --- 2
        "vib_turb_mancal_guia_x":  [0.05, 0.33],   # mm/s | OK end.19149 | atual: 0.3 mm/s
        "vib_turb_mancal_guia_y":  [0.05, 0.50],   # mm/s | RANGE AMPLIADO - lendo 0.35~0.41 | atual: 0.4 mm/s
    },
}
'''