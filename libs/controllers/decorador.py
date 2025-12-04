#decorador para mostrar o fluxo de execução e o tempo de execução de uma função

import functools
import time
import os

contador = 0

# Níveis de LOG:
# 0 = Desligado (sem logs)
# 1 = Decorador ligado (apenas tempo de execução)
# 2 = Decorador + prints detalhados de variáveis
LOGS_LEVEL = int(os.getenv("LOGS", "1"))

def desempenho(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global contador
        contador += 1
        
        if LOGS_LEVEL >= 1:
            # Extrai o nome do módulo/arquivo de forma segura
            modulo = func.__module__.split('.')[-1] if func.__module__ else 'desconhecido'
            # print('-' * 50)
            # print(f" {contador} - Função: {func.__name__} | Local: {modulo}")
        
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fim = time.time() - inicio
        
        # if LOGS_LEVEL >= 1:
        #     print(f"  {contador} - Tempo de execução: {fim} segundos")
        #     print('-' * 50)
        
        return resultado
    return wrapper