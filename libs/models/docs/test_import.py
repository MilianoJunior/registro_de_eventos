#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se os imports estão funcionando
"""
import sys
import os

# Adiciona o diretório raiz ao path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
sys.path.insert(0, ROOT_DIR)

print("Diretório do script:", SCRIPT_DIR)
print("Diretório raiz:", ROOT_DIR)
print("\nTestando imports...")

try:
    from libs.models.mock_data import DEVELOPER_MODE
    print("OK - Import mock_data: SUCESSO (DEVELOPER_MODE = {})".format(DEVELOPER_MODE))
except Exception as e:
    print("ERRO - Import mock_data: {}".format(e))
    DEVELOPER_MODE = None

try:
    from libs.models.database import Database
    print("OK - Import Database: SUCESSO")
except Exception as e:
    print("INFO - Import Database: {} (Normal em modo desenvolvedor)".format(e))

print("\n" + "="*60)
if DEVELOPER_MODE:
    print("⚠️  DEVELOPER_MODE está ATIVADO")
    print("    O sistema está usando dados mock")
    print("    Não é necessário executar migrações")
    print("\n    Para usar banco de dados real:")
    print("    1. Edite libs/models/mock_data.py")
    print("    2. Altere DEVELOPER_MODE = False")
    print("    3. Execute: python cog_schema.py migrate")
else:
    print("✅ DEVELOPER_MODE está DESATIVADO")
    print("    Sistema configurado para usar banco de dados")
    print("\n    Execute: python cog_schema.py migrate")
print("="*60)

