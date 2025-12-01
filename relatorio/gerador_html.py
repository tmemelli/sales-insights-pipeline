"""
Módulo: Geração de Relatório HTML
Responsável por consolidar métricas, insights e gráficos
em um relatório executivo pronto para portfólio.

Versão: 2.0 (Adaptado para estrutura achatada)
"""

from pathlib import Path
from typing import Dict, Any
import datetime as dt
import pandas as pd


class GeradorRelatorioHTML:
    """
    Gera um relatório HTML único em output/relatorio_vendas.html
    """

    def __init__(self, caminho_saida: str = "output/relatorio_vendas.html"):
        self.caminho_saida = Path(caminho_saida)
        self.caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    # ==================== Helpers ==================== #

    def _fmt_moeda(self, valor: Any) -> str:
        """Formata valor como moeda brasileira"""
        try:
            val = float(valor)
            return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return "R$ 0,00"

    def _fmt_numero(self, valor: Any, casas: int = 2) -> str:
        """Formata número com casas decimais"""
        try:
            return f"{float(valor):.{casas}f}"
        except Exception:
            return "0.00"

    # ==================== Geração ==================== #

    def gerar(
        self,
        df: pd.DataFrame,
        estatisticas: Dict[str, Any],
        insights: Dict[str, str],
        caminhos_graficos: Dict[str, str],
    ) -> Path:
        """
        Gera o relatório HTML final.
        
        Args:
            df: DataFrame limpo (não usado diretamente, mas mantido para compatibilidade)
            estatisticas: Dicionário com estatísticas (estrutura achatada)
            insights: Dicionário com insights {chave: mensagem_html}
            caminhos_graficos: Dicionário com caminhos dos gráficos
        
        Returns:
            Path do arquivo HTML gerado
        """
        
        # ========== Extração de Dados (estrutura achatada) ==========
        
        # Financeiro
        gmv = self._fmt_moeda(estatisticas.get("gmv", 0))
        lucro = self._fmt_moeda(estatisticas.get("lucro_estimado", 0))
        margem = self._fmt_numero(estatisticas.get("margem_media_percent", 0), 1) + "%"
        ticket = self._fmt_moeda(estatisticas.get("ticket_medio", 0))
        receita_media_dia = self._fmt_moeda(estatisticas.get("receita_media_diaria", 0))
        total_transacoes = int(estatisticas.get("total_transacoes", 0))
        total_unidades = int(estatisticas.get("total_unidades", 0))
        
        # Período
        data_inicio = estatisticas.get("data_inicio", "-")
        data_fim = estatisticas.get("data_fim", "-")
        dias_analisados = estatisticas.get("dias_analisados", 0)

        # Qualidade temporal
        dias_com_venda = estatisticas.get("dias_com_venda", 0)
        dias_periodo = estatisticas.get("dias_periodo", 0)
        densidade = self._fmt_numero(estatisticas.get("densidade_temporal_percent", 0), 1) + "%"

        # Top produtos (já vem como lista de tuplas)
        top_produtos = estatisticas.get("top_produtos", [])[:5]

        # Curva ABC (já vem como lista de tuplas: produto, receita, classe)
        curva_abc = estatisticas.get("curva_abc", [])[:5]

        # Top dias (já vem como lista de tuplas)
        top_dias = estatisticas.get("top_dias", [])[:5]

        # Insights em HTML
        insights_html = ""
        if insights:
            insights_html = "".join(f"<li>{texto}</li>" for texto in insights.values())
        else:
            insights_html = "<li>Nenhum insight calculado.</li>"

        # Gráficos (caminhos relativos)
        g_receita_diaria = caminhos_graficos.get("receita_diaria", "")
        g_receita_mensal = caminhos_graficos.get("receita_mensal", "")
        g_receita_semana = caminhos_graficos.get("receita_dia_semana", "")
        g_ticket = caminhos_graficos.get("distribuicao_ticket", "")
        g_ticket_seaborn = caminhos_graficos.get("distribuicao_ticket_seaborn", "")
        g_heatmap = caminhos_graficos.get("heatmap_mes_semana", "")

        # Data de geração
        gerado_em = dt.datetime.now().strftime("%d/%m/%Y às %H:%M")

        # ========== Template HTML ==========
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Vendas - {data_inicio} a {data_fim}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0f172a;
            color: #e5e7eb;
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #020617;
            border-radius: 18px;
            padding: 40px;
            box-shadow: 0 25px 60px rgba(0,0,0,0.6);
            border: 1px solid #1f2937;
        }}
        header {{
            border-bottom: 1px solid #1f2937;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2.2rem;
            color: #e5e7eb;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #9ca3af;
            font-size: 0.95rem;
        }}
        .badge {{
            display: inline-block;
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: #022c22;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 8px;
        }}
        .grid {{
            display: grid;
            gap: 20px;
            margin: 30px 0;
        }}
        .grid-3 {{
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        }}
        .grid-2 {{
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }}
        .card {{
            background: #020617;
            border-radius: 14px;
            padding: 20px;
            border: 1px solid #1f2937;
            transition: border-color 0.3s;
        }}
        .card:hover {{
            border-color: #374151;
        }}
        .card-kpi {{
            background: radial-gradient(circle at top left, #22c55e22, #020617);
        }}
        .card h2 {{
            font-size: 0.95rem;
            color: #9ca3af;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        .card .valor {{
            font-size: 1.8rem;
            font-weight: 600;
            color: #e5e7eb;
            margin-bottom: 4px;
        }}
        .card small {{
            color: #6b7280;
            font-size: 0.85rem;
        }}
        section {{
            margin-top: 40px;
        }}
        section h2.title {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #e5e7eb;
            font-weight: 600;
        }}
        img.grafico {{
            width: 100%;
            border-radius: 12px;
            margin-top: 12px;
            border: 1px solid #1f2937;
        }}
        ul {{
            list-style: disc;
            padding-left: 24px;
        }}
        li {{
            margin-bottom: 10px;
            color: #d1d5db;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }}
        th, td {{
            border-bottom: 1px solid #1f2937;
            padding: 10px 8px;
            font-size: 0.9rem;
            text-align: left;
        }}
        th {{
            color: #9ca3af;
            font-weight: 600;
        }}
        td {{
            color: #d1d5db;
        }}
        tr:hover td {{
            background: #1f2937;
        }}
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #1f2937;
            color: #6b7280;
            font-size: 0.9rem;
            text-align: center;
        }}
        .tag {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .tag-a {{ background: #22c55e33; color: #22c55e; }}
        .tag-b {{ background: #facc1533; color: #facc15; }}
        .tag-c {{ background: #fb923c33; color: #fb923c; }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>📊 Relatório de Vendas</h1>
        <p class="subtitle">
            Período: <strong>{data_inicio}</strong> até <strong>{data_fim}</strong>
            <span class="badge">{dias_analisados} dias</span>
        </p>
        <p class="subtitle" style="margin-top:6px;">
            Gerado em {gerado_em}
        </p>
    </header>

    <section>
        <h2 class="title">💰 Visão Geral Financeira</h2>
        <div class="grid grid-3">
            <div class="card card-kpi">
                <h2>GMV (Faturamento Bruto)</h2>
                <div class="valor">{gmv}</div>
                <small>Receita total no período</small>
            </div>
            <div class="card card-kpi">
                <h2>Lucro Estimado</h2>
                <div class="valor">{lucro}</div>
                <small>Baseado em margens por categoria</small>
            </div>
            <div class="card card-kpi">
                <h2>Margem Média</h2>
                <div class="valor">{margem}</div>
                <small>Lucro / GMV</small>
            </div>
            <div class="card">
                <h2>Ticket Médio</h2>
                <div class="valor">{ticket}</div>
                <small>Receita média por transação</small>
            </div>
            <div class="card">
                <h2>Receita Média Diária</h2>
                <div class="valor">{receita_media_dia}</div>
                <small>Média em {dias_analisados} dias</small>
            </div>
            <div class="card">
                <h2>Volume</h2>
                <div class="valor">{total_transacoes:,}</div>
                <small>{total_unidades:,} unidades vendidas</small>
            </div>
        </div>
    </section>

    <section>
        <h2 class="title">📈 Qualidade dos Dados</h2>
        <div class="grid grid-3">
            <div class="card">
                <h2>Dias com Vendas</h2>
                <div class="valor">{dias_com_venda}</div>
                <small>Dias com pelo menos 1 transação</small>
            </div>
            <div class="card">
                <h2>Dias no Período</h2>
                <div class="valor">{dias_periodo}</div>
                <small>Total de dias analisados</small>
            </div>
            <div class="card">
                <h2>Densidade Temporal</h2>
                <div class="valor">{densidade}</div>
                <small>Quanto mais próximo de 100%, melhor</small>
            </div>
        </div>
    </section>

    <section>
        <h2 class="title">🏆 Produtos em Destaque</h2>
        <div class="grid grid-2">
            <div class="card">
                <h2>Top 5 Produtos por Receita</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Produto</th>
                            <th style="text-align: right;">Receita</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(
                            f"<tr><td>{produto}</td><td style='text-align: right;'>{self._fmt_moeda(receita)}</td></tr>"
                            for produto, receita in top_produtos
                        ) if top_produtos else "<tr><td colspan='2'>Sem dados</td></tr>"}
                    </tbody>
                </table>
            </div>
            <div class="card">
                <h2>Curva ABC (Top 5)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Produto</th>
                            <th style="text-align: right;">Receita</th>
                            <th style="text-align: center;">Classe</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(
                            f"<tr><td>{produto}</td><td style='text-align: right;'>{self._fmt_moeda(receita)}</td>"
                            f"<td style='text-align: center;'><span class='tag tag-{classe.lower()}'>{classe}</span></td></tr>"
                            for produto, receita, classe in curva_abc
                        ) if curva_abc else "<tr><td colspan='3'>Sem dados</td></tr>"}
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <section>
        <h2 class="title">📅 Sazonalidade e Tendências</h2>
        <div class="grid grid-2">
            <div class="card">
                <h2>Receita Diária</h2>
                {f"<img src='{g_receita_diaria}' class='grafico' alt='Receita diária'>" if g_receita_diaria else "<p style='color: #6b7280; margin-top: 12px;'>Gráfico não disponível</p>"}
            </div>
            <div class="card">
                <h2>Receita Mensal</h2>
                {f"<img src='{g_receita_mensal}' class='grafico' alt='Receita mensal'>" if g_receita_mensal else "<p style='color: #6b7280; margin-top: 12px;'>Gráfico não disponível</p>"}
            </div>
        </div>
        <div class="grid grid-2">
            <div class="card">
                <h2>Receita por Dia da Semana</h2>
                {f"<img src='{g_receita_semana}' class='grafico' alt='Receita semanal'>" if g_receita_semana else "<p style='color: #6b7280; margin-top: 12px;'>Gráfico não disponível</p>"}
            </div>
            <div class="card">
                <h2>Distribuição do Ticket</h2>
                {f"<img src='{g_ticket}' class='grafico' alt='Distribuição ticket'>" if g_ticket else "<p style='color: #6b7280; margin-top: 12px;'>Gráfico não disponível</p>"}
            </div>
        </div>
        <div class="card" style="margin-top: 20px;">
            <h2>Distribuição do Ticket (Seaborn)</h2>
            {f"<img src='{g_ticket_seaborn}' class='grafico' alt='Distribuição Ticket Seaborn'>" if g_ticket_seaborn else "<p style='color: #6b7280; margin-top: 12px;'>Gráfico não disponível</p>"}
        </div>
        <div class="card" style="margin-top: 20px;">
            <h2>Heatmap (Dia da Semana × Mês)</h2>
            {f"<img src='{g_heatmap}' class='grafico' alt='Heatmap'>" if g_heatmap else "<p style='color: #6b7280; margin-top: 12px;'>Heatmap não disponível</p>"}
        </div>

        <div class="card" style="margin-top: 20px;">
            <h2>Top 5 Dias de Maior Receita</h2>
            <table>
                <thead>
                    <tr>
                        <th>Data</th>
                        <th style="text-align: right;">Receita</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(
                        f"<tr><td>{data}</td><td style='text-align: right;'>{self._fmt_moeda(receita)}</td></tr>"
                        for data, receita in top_dias
                    ) if top_dias else "<tr><td colspan='2'>Sem dados</td></tr>"}
                </tbody>
            </table>
        </div>
    </section>

    <section>
        <h2 class="title">💡 Insights Automáticos</h2>
        <div class="card">
            <ul>
                {insights_html}
            </ul>
        </div>
    </section>

    <footer>
        <p><strong>🤖 Relatório gerado automaticamente pelo Analisador de Vendas</strong></p>
        <p>Desenvolvido por <strong>Thiago Memelli</strong> | 
           <a href="https://github.com/tmemelli" style="color: #22c55e; text-decoration: none;">@tmemelli</a>
        </p>
        <p style="margin-top: 8px; font-size: 0.85rem;">
            Tecnologias: Python • Pandas • Matplotlib • Seaborn
        </p>
    </footer>
</div>
</body>
</html>
"""

        # Salva o arquivo
        with self.caminho_saida.open("w", encoding="utf-8") as f:
            f.write(html)

        print(f"\n✅ Relatório HTML gerado: {self.caminho_saida}")
        print(f"📂 Abra no navegador: file:///{self.caminho_saida.absolute()}\n")
        
        return self.caminho_saida