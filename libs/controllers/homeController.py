# libs/controllers/homeController.py
from collections import Counter
from flask import render_template
from libs.models.read import Read
from libs.models.mock_data import DEVELOPER_MODE, get_estatisticas_home
from libs.models.utils.utils import desempenho

class HomeController:
    def __init__(self):
        self.ocorrencias = Read("op_ocorrencia")
        self.usinas = Read("op_usina")
        self._cache = {}  # cache para dados do banco
        self.developer = True

    @desempenho
    def _get_or_set(self, key, loader):
        """Método auxiliar para cache de dados"""
        if key not in self._cache:
            self._cache[key] = loader()
        return self._cache[key]

    @desempenho
    def home(self):
        """Renderiza a página home com estatísticas"""
        if DEVELOPER_MODE:
            # Usa dados mock do arquivo mock_data.py
            stats = get_estatisticas_home()
            usinas = stats['usinas']
            recentes = stats['recentes']
            status = stats['status']
            por_unidade = stats['por_unidade']
            total_ocorrencias = stats['total_ocorrencias']
        else:
            # Usa dados reais do banco de dados
            usinas = self._get_or_set("usinas", lambda: self.usinas.get_all())
            rows = self._get_or_set("ocorrencias", lambda: self.ocorrencias.get_all(limit=20))

            recentes = sorted(rows, key=lambda r: r.get("created_at"), reverse=True)[:10]
            status = Counter((r.get("status") or "-") for r in rows)
            unidades = Counter((r.get("unidade") or "-") for r in rows)
            por_unidade = sorted(unidades.items(), key=lambda x: (-x[1], x[0]))[:8]
            total_ocorrencias = len(rows)

        return render_template("home.html",
            usinas=usinas,
            total_ocorrencias=total_ocorrencias,
            recentes=recentes,
            por_status=dict(status),
            por_unidade=por_unidade,
        )
