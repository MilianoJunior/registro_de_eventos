# libs/models/create.py
from __future__ import annotations
from typing import Optional, Dict, Any
from libs.models.database import Database

class Create:
    """
    Repositório de criação/inserção simples (parametrizado, reutilizável).
    """
    def __init__(
        self,
        tabela: str,
        db_instance: Optional[Database] = None,
    ):
        self.tabela = tabela
        self.db = db_instance or Database()

    def insert(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Insere um novo registro na tabela.
        
        Args:
            data: Dicionário com os dados a serem inseridos (coluna: valor)
            
        Returns:
            ID do registro inserido ou None em caso de erro
        """
        try:
            self.db.connect()
            
            # Prepara as colunas e valores
            columns = list(data.keys())
            values = list(data.values())
            
            # Monta a query SQL
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join([f"`{col}`" for col in columns])
            
            sql = f"INSERT INTO `{self.tabela}` ({columns_str}) VALUES ({placeholders})"
            
            # Executa a query
            cursor = self.db.execute_query(sql, tuple(values))
            
            if cursor:
                # Retorna o ID do último registro inserido
                return cursor.lastrowid
            
            return None
            
        except Exception as e:
            self._error('Create', 'insert', e)
            return None

    def insert_many(self, data_list: list[Dict[str, Any]]) -> Optional[int]:
        """
        Insere múltiplos registros de uma vez.
        
        Args:
            data_list: Lista de dicionários com os dados a serem inseridos
            
        Returns:
            Número de registros inseridos ou None em caso de erro
        """
        try:
            if not data_list:
                return 0
                
            self.db.connect()
            
            # Pega as colunas do primeiro registro
            columns = list(data_list[0].keys())
            columns_str = ", ".join([f"`{col}`" for col in columns])
            placeholders = ", ".join(["%s"] * len(columns))
            
            sql = f"INSERT INTO `{self.tabela}` ({columns_str}) VALUES ({placeholders})"
            
            # Prepara os valores de todos os registros
            values_list = [tuple(item[col] for col in columns) for item in data_list]
            
            # Executa a query para cada registro
            count = 0
            for values in values_list:
                cursor = self.db.execute_query(sql, values)
                if cursor:
                    count += 1
            
            return count
            
        except Exception as e:
            self._error('Create', 'insert_many', e)
            return None

    def _error(self, name, function, e):
        raise Exception(f"Erro: class: {name}, function: {function}: msg: {e}")


# ----------------- Models específicos -----------------
class OpUsinaCreate(Create):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_usina", db_instance=db_instance)

class OpUsuarioCreate(Create):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_usuario", db_instance=db_instance)

class OpOcorrenciaCreate(Create):
    def __init__(self, db_instance: Optional[Database] = None):
        super().__init__("op_ocorrencia", db_instance=db_instance)

