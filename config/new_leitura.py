# ips_pch_pira = {
#     "GERAL": {
#         "SUPERVISORIO": "10.200.20.5",
#         "MASK": "255.255.255.0",
#         "GATEWAY": "10.200.20.1"
#     },
#     "UG01": {
#         "CLP": "10.200.20.11",
#         "QCC-UG01": "10.200.20.14",
#         "IHM": "10.200.20.12",
#         "RELE": "10.200.20.13",
#     },
#     "PSA": {
#         "CLP": "10.200.20.61",
#         "IHM": "10.200.20.62",
#         "RELE 787": "10.200.20.63",
#         "RELE 751": "10.200.20.64",
#         "GMG": "10.200.20.65"
#     }
# }

MAPEAMENTO_UG01 = {
    "10.200.20.11": {  # CLP / UG1_Medida / MDB_Medidas / MdbMeter
        "potencia_ativa":        [2588, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "potencia_reativa":      [2590, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "fator_potencia":        [2594, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "horimetro_gerador":     [2648, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "energia_acumulada":     [2652, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "tensao":                [2574, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "corrente":              [2582, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "freq":                  [2560, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

        "excitacao_corrente":    [2602, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "excitacao_disparo":     [19195, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "temp_ponte_tiristores": [2642, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],


        "pressao_oleo_uhrv":     [19135, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "pressao_oleo_uhlm":     [19117, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

        "vib_ger_mancal_guia_x": [19163, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "vib_ger_mancal_guia_y": [19167, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "vib_ger_mancal_comb_x": [19171, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "vib_ger_mancal_comb_y": [19175, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "vib_ger_mancal_comb_z": [19179, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

        "vib_turb_mancal_guia_x": [19149, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "vib_turb_mancal_guia_y": [19153, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

        "pressao_conduto":       [19145, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "rotacao":               [2628, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "pos_distribuidor":      [2632, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "pos_rotor":             [2636, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],


        # --- UHRV / UHLM ---
        "temp_oleo_uhrv":          [19619, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "temp_oleo_uhlm":          [19623, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

    },
     "10.200.20.61": {
            # --- Níveis (PSA - melhores matches reais) --- 3
            "nivel_camara_carga": [19381, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # 390.46
            "nivel_barragem":     [19393, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # 390.45
            "nivel_jusante":      [19171, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],  # faixa válida   

        },

    "10.200.20.5": {  # QCC-UG01 / QCC_Medida
        "nivel_camara_carga":    [21787, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "nivel_barragem":        [21793, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

        # corrigido com base no QCC_Medida
        "nivel_jusante_sensor":  [19101, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        "nivel_jusante":         [19103, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    },

    "10.200.20.13": {  # RELE / SEL700G_Leituras
        # tipo ainda precisa ser validado no driver, porque no arquivo aparece WORD
        # "temp_ger_fase_r":          [400490, "WORD", {"slave": 2}],
        # "temp_ger_fase_s":          [400491, "WORD", {"slave": 2}],
        # "temp_ger_fase_t":          [400492, "WORD", {"slave": 2}],
        # "temp_ger_nucleo":          [400493, "WORD", {"slave": 2}],
        # "temp_mancal_guia_ger":     [400494, "WORD", {"slave": 2}],
        # "temp_mancal_comb_casq":    [400495, "WORD", {"slave": 2}],
        # "temp_mancal_comb_escora":  [400496, "WORD", {"slave": 2}],
        # "temp_mancal_comb_contra":  [400497, "WORD", {"slave": 2}],
        # "temp_mancal_guia_turb_1":  [400498, "WORD", {"slave": 2}],
        # "temp_oleo_uhrv":           [400500, "WORD", {"slave": 2}],
        # "temp_oleo_uhlm":           [400501, "WORD", {"slave": 2}],
                # --- Temperaturas Gerador (candidatas mais coerentes) ---
        # "temp_ger_fase_r":        [400490, "INT", {"offset": 0, "converter": "word_order"}],
        # "temp_ger_fase_s":        [400491, "INT", {"offset": 0, "converter": "word_order"}],
        # "temp_ger_fase_t":        [400492, "INT", {"offset": 0, "converter": "word_order"}],
        # "temp_ger_nucleo":        [400493, "INT", {"offset": 0, "converter": "word_order"}],

        # # --- Temperaturas Mancais Gerador ---
        # "temp_mancal_comb_escora": [2620, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        # "temp_mancal_comb_casq":   [2622, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        # "temp_mancal_comb_contra": [2624, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        # "temp_mancal_guia_ger":    [2626, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],

        # # --- Temperaturas Mancal Turbina ---
        # "temp_mancal_guia_turb_1": [2628, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
        # "temp_mancal_guia_turb_2": [2630, "INPUT_REAL", {"offset": 0, "converter": "word_order"}],
    }
}