
from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from libs.models.database import Database


class BaseCrud:
    """Classe base para operações CRUD genéricas."""

    tabela: str
    colunas: List[str]

    def __init__(self) -> None:
        self.db = Database()
        self._colunas_set = set(self.colunas)

    def _validate_columns(self, columns: Union[str, List[str]]) -> List[str]:
        """Valida e normaliza lista de colunas. Suporta '*' para todas as colunas."""
        if columns == "*" or columns == ["*"]:
            return self.colunas[:]

        if isinstance(columns, str):
            columns = [columns]

        columns = [col.strip() for col in columns]
        if not all(col in self._colunas_set for col in columns):
            raise ValueError(f"Colunas inválidas: {set(columns) - self._colunas_set}")
        return columns

    def read(
        self,
        columns: Union[str, List[str]] = "*",
        where: Optional[str] = None,
        where_params: Optional[Sequence[Any]] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Busca registros com colunas selecionadas."""
        columns = self._validate_columns(columns)
        query = f"SELECT {', '.join(columns)} FROM {self.tabela}"

        params: List[Any] = []
        if where:
            query += f" WHERE {where}"
            if where_params:
                params.extend(where_params)

        if order:
            query += f" ORDER BY {order}"
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        return self.db.fetch_data(query, tuple(params))

    def create(self, data: Dict[str, Any]) -> int:
        """Insere um novo registro e retorna o número de linhas afetadas."""
        valid_data = {k: v for k, v in data.items() if k in self._colunas_set}
        if not valid_data:
            raise ValueError("Nenhum dado válido para inserir")

        columns = ', '.join(valid_data.keys())
        placeholders = ', '.join(['%s'] * len(valid_data))
        query = f"INSERT INTO {self.tabela} ({columns}) VALUES ({placeholders})"

        return self.db.execute_query(query, tuple(valid_data.values()))

    def update(
        self,
        data: Dict[str, Any],
        where: str,
        where_params: Optional[Sequence[Any]] = None,
    ) -> int:
        """Atualiza registros conforme cláusula WHERE."""
        valid_data = {k: v for k, v in data.items() if k in self._colunas_set}
        if not valid_data:
            raise ValueError("Nenhum dado válido para atualizar")

        set_clause = ', '.join(f"{k} = %s" for k in valid_data.keys())
        query = f"UPDATE {self.tabela} SET {set_clause} WHERE {where}"

        params = list(valid_data.values())
        if where_params:
            params.extend(where_params)

        return self.db.execute_query(query, tuple(params))

    def delete(
        self,
        where: str,
        where_params: Optional[Sequence[Any]] = None,
    ) -> int:
        """Remove registros conforme cláusula WHERE."""
        if not where:
            raise ValueError("Cláusula WHERE é obrigatória para DELETE")

        query = f"DELETE FROM {self.tabela} WHERE {where}"
        return self.db.execute_query(query, tuple(where_params) if where_params else None)

    def count(
        self,
        where: Optional[str] = None,
        where_params: Optional[Sequence[Any]] = None,
    ) -> int:
        """Retorna a contagem de registros."""
        query = f"SELECT COUNT(*) AS total FROM {self.tabela}"
        params: List[Any] = []

        if where:
            query += f" WHERE {where}"
            if where_params:
                params.extend(where_params)

        result = self.db.fetch_data(query, tuple(params))
        return result[0]["total"] if result else 0


# ====================== Classes específicas ======================

class Clientes(BaseCrud):
    tabela = "clientes"
    colunas = ["id", "nome_razao", "cnpj", "cidade", "obras"]


class Usuarios(BaseCrud):
    tabela = "op_usuario"
    colunas = ["id", "nome", "email", "perfil", "ativo", "cargo", "assinatura"]


class Rat(BaseCrud):
    tabela = "rats"
    colunas = [
        "id", "protocolo", "data_emissao", "cliente_id", "obra_nome",
        "num_proposta", "num_contrato", "data_solicitacao", "solicitante",
        "tipo_atividade", "prioridade", "em_garantia", "relato_cliente",
        "tecnico_id", "descricao_atividades", "conclusao",
        "caminho_assinatura_tec", "caminho_assinatura_cli", "status_financeiro", "deslocamento"
    ]

    # Métodos específicos (todos parametrizados quando possível)
    def get_total_rats_month(self) -> int:
        query = """
            SELECT COUNT(*) AS total 
            FROM rats 
            WHERE MONTH(data_emissao) = MONTH(CURRENT_DATE()) 
              AND YEAR(data_emissao) = YEAR(CURRENT_DATE())
        """
        res = self.db.fetch_data(query)
        return res[0]["total"] if res else 0

    def get_total_hours_month(self) -> float:
        query = """
            SELECT COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(s.hora_fim, s.hora_inicio))) / 3600, 0) AS total_hours
            FROM rat_servicos s
            JOIN rats r ON s.rat_id = r.id
            WHERE MONTH(r.data_emissao) = MONTH(CURRENT_DATE())
              AND YEAR(r.data_emissao) = YEAR(CURRENT_DATE())
        """
        res = self.db.fetch_data(query)
        return float(res[0]["total_hours"]) if res else 0.0

    def get_top_plant_hours(self) -> Optional[Dict[str, Any]]:
        query = """
            SELECT r.obra_nome,
                   COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(s.hora_fim, s.hora_inicio))) / 3600, 0) AS total_hours
            FROM rats r
            JOIN rat_servicos s ON r.id = s.rat_id
            GROUP BY r.obra_nome
            ORDER BY total_hours DESC
            LIMIT 1
        """
        res = self.db.fetch_data(query)
        return res[0] if res else None

    def get_rats_with_hours_paginated(self, limit: int, offset: int, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        where_clause = ""
        params = []
        
        if search_term:
            term = f"%{search_term}%"
            where_clause = "WHERE (r.protocolo LIKE %s OR r.obra_nome LIKE %s OR r.solicitante LIKE %s OR r.relato_cliente LIKE %s)"
            params.extend([term, term, term, term])

        query = f"""
            SELECT r.*,
                   COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(s.hora_fim, s.hora_inicio))) / 3600, 0) AS total_horas
            FROM {self.tabela} r
            LEFT JOIN rat_servicos s ON r.id = s.rat_id
            {where_clause}
            GROUP BY r.id
            ORDER BY r.data_emissao DESC, r.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return self.db.fetch_data(query, tuple(params))

    def get_average_time_rat(self) -> float:
        query = """
            SELECT AVG(rat_hours) AS avg_hours
            FROM (
                SELECT SUM(TIME_TO_SEC(TIMEDIFF(hora_fim, hora_inicio))) / 3600 AS rat_hours
                FROM rat_servicos
                GROUP BY rat_id
            ) AS subquery
        """
        res = self.db.fetch_data(query)
        return float(res[0]["avg_hours"]) if res and res[0]["avg_hours"] is not None else 0.0

    def get_pending_signatures_count(self) -> int:
        query = """
            SELECT COUNT(*) AS total
            FROM rats
            WHERE caminho_assinatura_tec IS NULL OR caminho_assinatura_tec = ''
               OR caminho_assinatura_cli IS NULL OR caminho_assinatura_cli = ''
        """
        res = self.db.fetch_data(query)
        return res[0]["total"] if res else 0

    def get_priority_distribution(self) -> List[Dict[str, Any]]:
        query = f"SELECT prioridade, COUNT(*) AS count FROM {self.tabela} WHERE prioridade IS NOT NULL GROUP BY prioridade"
        return self.db.fetch_data(query)

    def get_activity_list(self) -> List[Dict[str, Any]]:
        query = f"""
            SELECT tipo_atividade, COUNT(*) AS count
            FROM {self.tabela}
            WHERE tipo_atividade IS NOT NULL
            GROUP BY tipo_atividade
            ORDER BY count DESC
        """
        return self.db.fetch_data(query)

    def get_tech_hours(self) -> List[Dict[str, Any]]:
        query = """
            SELECT u.nome,
                   COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(s.hora_fim, s.hora_inicio))) / 3600, 0) AS total_hours
            FROM rat_servicos s
            JOIN op_usuario u ON s.executante_id = u.id
            GROUP BY u.nome
            ORDER BY total_hours DESC
        """
        return self.db.fetch_data(query)

    def get_top_clients(self) -> List[Dict[str, Any]]:
        query = """
            SELECT obra_nome, COUNT(*) AS count
            FROM rats
            WHERE obra_nome IS NOT NULL
            GROUP BY obra_nome
            ORDER BY count DESC
            LIMIT 5
        """
        return self.db.fetch_data(query)

    def get_by_id_with_details(self, rat_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT r.*, 
                   c.nome_razao AS cliente_nome, 
                   c.cnpj AS cliente_cnpj, 
                   c.cidade AS cliente_cidade,
                   u.nome AS tecnico_nome
            FROM rats r
            LEFT JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN op_usuario u ON r.tecnico_id = u.id
            WHERE r.id = %s
        """
        res = self.db.fetch_data(query, (rat_id,))
        return res[0] if res else None


class RatServicos(BaseCrud):
    tabela = "rat_servicos"
    colunas = ["id", "rat_id", "data_servico", "hora_inicio", "hora_fim", "executante_id", "observacoes"]

    def get_by_rat_id_with_executante(self, rat_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT s.*, u.nome AS executante_nome
            FROM rat_servicos s
            LEFT JOIN op_usuario u ON s.executante_id = u.id
            WHERE s.rat_id = %s
        """
        return self.db.fetch_data(query, (rat_id,))

class RatMateriais(BaseCrud):
    tabela = "rat_materiais"
    colunas = ["id", "rat_id", "codigo_engesep", "descricao", "fabricante", "quantidade", "unidade"]


class RatFotos(BaseCrud):
    tabela = "rat_fotos"
    colunas = ["id", "rat_id", "caminho_arquivo", "legenda", "ordem"]


class Produtos(BaseCrud):
    tabela = "produtos"
    colunas = ["id", "codigo_produto", "descricao", "unidade", "marca", "preco_venda"]

    def search_by_term(self, term: str, limit: int = 20) -> List[Dict[str, Any]]:
        safe_term = term.replace("'", "''")  # escape básico
        query = f"""
            SELECT * FROM {self.tabela}
            WHERE descricao LIKE %s OR codigo_produto LIKE %s
            LIMIT %s
        """
        pattern = f"%{safe_term}%"
        return self.db.fetch_data(query, (pattern, pattern, limit))