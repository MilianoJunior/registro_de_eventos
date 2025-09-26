from flask import render_template
from libs.models.read import Read

class HomeController:
    def __init__(self):
        self.ocorrencias = Read('op_ocorrencia')
        self.usinas = Read('op_usina')

    def home(self):
        usinas = self.usinas.get_all()

        rows = self.ocorrencias.get_all(limit=20)
        recentes = sorted(rows, key=lambda r: r.get("created_at"), reverse=True)[:10]
        por_status, por_unidade = {}, {}
        for r in rows:
            por_status[r.get("status") or "-"] = por_status.get(r.get("status") or "-", 0) + 1
            un = r.get("unidade") or "-"
            por_unidade[un] = por_unidade.get(un, 0) + 1

        ctx = {
            "usinas": usinas,                           # <-- AQUI
            "total_ocorrencias": len(rows),
            "recentes": recentes,
            "por_status": por_status,
            "por_unidade": sorted(por_unidade.items(), key=lambda x: (-x[1], x[0]))[:8],
        }
        return render_template('home.html', **ctx)


