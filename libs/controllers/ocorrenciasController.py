# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _bool_para_int → normaliza flags (true/false) para 1/0 (MySQL)
# 2. _datetime_local_para_mysql → converte datetime-local (HTML) para datetime do MySQL
# 3. OcorrenciasController → página e APIs de ocorrências (listar/criar/resolver)
# -------------------------------------------------------------------

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from flask import jsonify, render_template, request

from libs.controllers.decorador import desempenho
from libs.models.create import OpOcorrenciaCreate
from libs.models.edit import OpOcorrenciaEdit
from libs.models.modelstate import DadosContexto, OcorrenciasPageViewModel
from libs.models.read import OpOcorrencia
from libs.models.utils.mock_data import DEVELOPER_MODE
from libs.models.utils.utils import build_where_clause, columns_sql, limit_sql, order_sql, safe_ident


def _bool_para_int(v: Any) -> int:
    if isinstance(v, bool):
        return 1 if v else 0
    s = str(v).strip().lower()
    return 1 if s in ("1", "true", "sim", "yes", "on") else 0


def _datetime_local_para_mysql(valor: Any) -> Optional[str]:
    """
    datetime-local (HTML): 'YYYY-MM-DDTHH:MM'
    MySQL datetime:        'YYYY-MM-DD HH:MM:SS'
    """
    if not valor:
        return None
    s = str(valor).strip()
    if not s:
        return None
    if "T" in s:
        s = s.replace("T", " ", 1)
    return (s + ":00") if len(s) == 16 else s


class OcorrenciasController:
    def __init__(self):
        self.ocorrencias_create: Optional[OpOcorrenciaCreate] = None
        self.ocorrencias_read: Optional[OpOcorrencia] = None
        self.ocorrencias_edit: Optional[OpOcorrenciaEdit] = None

        if DEVELOPER_MODE:
            return

        self.ocorrencias_create = OpOcorrenciaCreate()
        self.ocorrencias_read = OpOcorrencia()
        self.ocorrencias_edit = OpOcorrenciaEdit()

    @desempenho
    def ocorrencias_page(self):
        """Renderiza a página de ocorrências usando ViewModel"""
        inicio = time.time()

        ctx = DadosContexto()
        vm = OcorrenciasPageViewModel.carregar(ctx)

        fim = time.time()
        print(f"ocorrenciasController.ocorrencias_page - Tempo de execução: {fim - inicio} segundos")
        return render_template(
            "ocorrencias.html",
            vm=vm,
            usinas=vm.usinas,
            usuarios=vm.usuarios,
            templates=vm.templates,
            categorias=vm.categorias,
            tipos=vm.tipos,
        )

    @desempenho
    def listar_ocorrencias(self):
        """API: lista ocorrências (GET) com filtros via querystring"""
        try:
            status_filter = request.args.get("status")
            requer_acao = request.args.get("requer_acao")
            limit = request.args.get("limit", type=int, default=50) or 50
            limit = max(1, min(int(limit), 500))

            if DEVELOPER_MODE:
                from libs.models.utils.mock_data import get_mock_data
                rows = list(get_mock_data("op_ocorrencia") or [])
                rows = self._filtrar_mock(rows, status_filter, requer_acao)
                return jsonify(rows[:limit])

            where: Dict[str, Any] = {}
            if status_filter:
                lista_status = [s.strip() for s in status_filter.split(",") if s.strip()]
                if len(lista_status) == 1:
                    where["status"] = lista_status[0]
                elif len(lista_status) > 1:
                    where["status__in"] = lista_status

            if requer_acao is not None:
                where["requer_acao"] = _bool_para_int(requer_acao)

            assert self.ocorrencias_read is not None
            cols = columns_sql(self.ocorrencias_read.colunas_padrao)
            sql = f"SELECT {cols} FROM {safe_ident(self.ocorrencias_read.tabela)}"
            where_sql, params = build_where_clause(where)
            sql += where_sql
            sql += order_sql("created_at", True)
            sql += limit_sql(limit, None)

            rows = self.ocorrencias_read._run(sql, tuple(params))
            rows = self.ocorrencias_read._injetar_usina_nome(rows)
            return jsonify(rows)

        except Exception as e:
            print(f"[ERRO] listar_ocorrencias: {e}")
            return jsonify({"error": str(e)}), 500

    @desempenho
    def get_ocorrencias(self):
        """Compat: alias para listagem antiga (/api/ocorrencias)."""
        return self.listar_ocorrencias()

    @desempenho
    def criar_ocorrencia(self):
        """API: cria ocorrência (POST JSON)"""
        try:
            data = request.get_json(silent=True) or {}

            required_fields = ["usina_id", "operador_id", "tipo", "categoria", "unidade", "descricao", "data_ocorrencia"]
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"success": False, "error": f"Campo obrigatório: {field}"}), 400

            requer_acao = bool(data.get("requer_acao", False))
            metadata = {
                "requer_acao": requer_acao,
                "notificado_em": None,
                "responsavel_id": None,
                "assumido_em": None,
                "observacoes": None,
            }

            ocorrencia_data = {
                "usina_id": int(data["usina_id"]),
                "operador_id": int(data["operador_id"]),
                "tipo": str(data["tipo"]),
                "categoria": str(data["categoria"]),
                "unidade": str(data["unidade"]),
                "tags": str(data.get("tags", "")),
                "playbook": str(data.get("playbook", "")),
                "template_texto": str(data.get("template_texto", "")),
                "descricao": str(data["descricao"]),
                "status": "aberta",
                "severidade": str(data.get("severidade", "média")),
                "origem": "humano",
                "metadata": json.dumps(metadata, ensure_ascii=False),
                "requer_acao": 1 if requer_acao else 0,
                "data_ocorrencia": _datetime_local_para_mysql(data.get("data_ocorrencia")),
            }

            for key, value in ocorrencia_data.items():
                print(f"{key}: {value}")

            if DEVELOPER_MODE:
                return jsonify({"success": True, "message": "Ocorrência registrada (mock)", "id": 0}), 201

            assert self.ocorrencias_create is not None
            ocorrencia_id = self.ocorrencias_create.insert(ocorrencia_data)
            if not ocorrencia_id:
                return jsonify({"success": False, "error": "Erro ao registrar ocorrência"}), 500

            return jsonify({"success": True, "message": "Ocorrência registrada com sucesso!", "id": ocorrencia_id}), 201

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @desempenho
    def resolver_ocorrencia(self, ocorrencia_id: int):
        """API: resolve ocorrência (PUT/POST JSON)"""
        try:
            data = request.get_json(silent=True) or {}

            required_fields = ["resolvida_por", "data_resolucao", "resolucao_descricao"]
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"success": False, "error": f"Campo obrigatório: {field}"}), 400

            if DEVELOPER_MODE:
                return jsonify({"success": True, "message": "Ocorrência resolvida (mock)"}), 200

            assert self.ocorrencias_edit is not None
            rows = self.ocorrencias_edit.update_by_id(
                int(ocorrencia_id),
                {
                    "status": "resolvida",
                    "resolvida_por": int(data["resolvida_por"]),
                    "resolucao_descricao": str(data["resolucao_descricao"]),
                    "resolved_at": _datetime_local_para_mysql(data.get("data_resolucao")),
                },
            )

            if rows <= 0:
                return jsonify({"success": False, "error": "Ocorrência não encontrada"}), 404

            return jsonify({"success": True, "message": "Ocorrência resolvida com sucesso!"}), 200

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    def _filtrar_mock(self, rows: List[Dict[str, Any]], status_filter: Optional[str], requer_acao: Optional[str]) -> List[Dict[str, Any]]:
        if status_filter:
            lista_status = [s.strip() for s in status_filter.split(",") if s.strip()]
            rows = [r for r in rows if (r.get("status") in lista_status)]
        if requer_acao is not None:
            flag = _bool_para_int(requer_acao)
            rows = [r for r in rows if _bool_para_int(r.get("requer_acao")) == flag]
        return rows
