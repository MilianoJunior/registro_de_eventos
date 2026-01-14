# -------------------------------------------------------------------
# FLUXO DO MÓDULO
# 1. _bool_para_int → normaliza flags (true/false) para 1/0 (MySQL)
# 2. _datetime_local_para_mysql → converte datetime-local (HTML) para datetime do MySQL
# 3. OcorrenciasController → página e APIs de ocorrências (listar/criar/resolver)
# -------------------------------------------------------------------

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from flask import jsonify, render_template, request

from libs.controllers.decorador import desempenho
from libs.models.create import OpOcorrenciaCreate
from libs.models.edit import OpOcorrenciaEdit
from libs.models.modelstate import DadosContexto, OcorrenciasPageViewModel
from libs.models.read import OpOcorrencia

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
        self.ocorrencias_create = OpOcorrenciaCreate()
        self.ocorrencias_read = OpOcorrencia()
        self.ocorrencias_edit = OpOcorrenciaEdit()

    @desempenho
    def ocorrencias_page(self):
        """Renderiza a página de ocorrências usando ViewModel"""
        ctx = DadosContexto()
        vm = OcorrenciasPageViewModel.carregar(ctx)
        return render_template(
            "ocorrencias.html",
            usinas=vm.usinas,
            usuarios=vm.usuarios,
            templates=vm.templates,
            categorias=vm.categorias,
            tipos=vm.tipos,
            ocorrencias_requer_acao=vm.ocorrencias_requer_acao,
        )

    @desempenho
    def listar_ocorrencias(self):
        """API: lista ocorrências (GET) com filtros via querystring"""
        try:
            status_filter = request.args.get("status")
            requer_acao = request.args.get("requer_acao")
            ctx = DadosContexto()
            if requer_acao is not None and _bool_para_int(requer_acao) == 1 and not status_filter:
                return jsonify(ctx.get_ocorrencias_requer_acao())

            status_list = None
            if status_filter:
                status_list = [s.strip() for s in status_filter.split(",") if s.strip()]

            requer_acao_val = None
            if requer_acao is not None:
                requer_acao_val = _bool_para_int(requer_acao)

            limit = int(request.args.get("limit", 50))
            rows = self.ocorrencias_read.listar_api(
                status_list=status_list,
                requer_acao=requer_acao_val,
                limit=limit
            )
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

            requer_acao = bool(data.get("requer_acao", False))
            metadata = {}

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
                "status": "aberta" if requer_acao else "cancelada",
                "severidade": str(data.get("severidade", "média")),
                "origem": "humano",
                "metadata": json.dumps(metadata, ensure_ascii=False),
                "requer_acao": 1 if requer_acao else 0,
                "data_ocorrencia": _datetime_local_para_mysql(data.get("data_ocorrencia")),
            }
            ocorrencia_id = self.ocorrencias_create.insert(ocorrencia_data)
            if not ocorrencia_id:
                return jsonify({"success": False, "error": "Erro ao registrar ocorrência"}), 500

            # Invalida cache para que a listagem atualize
            DadosContexto().invalidar_cache_ocorrencias()
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

            # 1. Verifica se existe
            existente = self.ocorrencias_read.one({"id": int(ocorrencia_id)})
            if not existente:
                return jsonify({"success": False, "error": "Ocorrência não encontrada"}), 404
            if not existente.get("requer_acao"):
                return jsonify({"success": False, "error": "Ocorrência não requer ação"}), 400

            # 2. Tenta atualizar
            rows = self.ocorrencias_edit.update_by_id(
                int(ocorrencia_id),
                {
                    "status": "resolvida",
                    "resolvida_por": int(data["resolvida_por"]),
                    "resolucao_descricao": str(data["resolucao_descricao"]),
                    "resolved_at": _datetime_local_para_mysql(data.get("data_resolucao")),
                    "requer_acao": 0,
                },
            )

            # Se rows for 0, mas o registro existe, é pq não houve mudança (idempotente) -> Sucesso
            # Se rows for 0, mas o registro existe, é pq não houve mudança (idempotente) -> Sucesso
            DadosContexto().invalidar_cache_ocorrencias()
            return jsonify({"success": True, "message": "Ocorrência resolvida com sucesso!", "refresh": True}), 200

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500