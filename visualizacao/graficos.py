"""
Módulo: Geração de Gráficos
Responsável por criar visualizações dos dados de vendas
e salvar como arquivos de imagem (PNG) para uso no relatório.
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


class GraficosVendas:
    """
    Classe responsável por gerar gráficos a partir do DataFrame limpo.
    """

    def __init__(self, pasta_saida: str = "output/graficos"):
        self.pasta_saida = Path(pasta_saida)
        self.pasta_saida.mkdir(parents=True, exist_ok=True)

        # Configuração visual geral
        plt.rcParams["figure.figsize"] = (12, 6)
        plt.rcParams["axes.grid"] = True
        plt.rcParams["font.size"] = 10

    def _salvar_figura(self, nome_arquivo: str):
        caminho = self.pasta_saida / nome_arquivo
        plt.tight_layout()
        plt.savefig(caminho, dpi=150, bbox_inches="tight")
        plt.close()
        return caminho

    # ------------------------------------------------------------------ #
    # Gráficos principais
    # ------------------------------------------------------------------ #

    def grafico_receita_diaria(self, df: pd.DataFrame) -> Path:
        """Linha de receita por dia (visão geral do ano)."""
        receita_diaria = df.groupby("data")["receita"].sum()

        plt.figure()
        plt.plot(receita_diaria.index, receita_diaria.values, linewidth=1.8)
        plt.title("Evolução da Receita Diária")
        plt.xlabel("Data")
        plt.ylabel("Receita (R$)")
        plt.xticks(rotation=45)
        return self._salvar_figura("receita_diaria.png")

    def grafico_receita_mensal(self, df: pd.DataFrame) -> Path:
        """Barra de receita mensal."""
        receita_mensal = (
            df.groupby(["ano", "mes"])["receita"]
            .sum()
            .reset_index()
            .sort_values(["ano", "mes"])
        )
        # cria coluna ano-mês no formato 2024-01
        receita_mensal["ano_mes"] = receita_mensal.apply(
            lambda x: f"{int(x['ano'])}-{int(x['mes']):02d}", axis=1
        )

        plt.figure()
        plt.bar(receita_mensal["ano_mes"], receita_mensal["receita"])
        plt.title("Receita Mensal")
        plt.xlabel("Mês")
        plt.ylabel("Receita (R$)")
        plt.xticks(rotation=45)
        return self._salvar_figura("receita_mensal.png")

    def grafico_receita_por_dia_semana(self, df: pd.DataFrame) -> Path:
        """Barra de receita agregada por dia da semana."""
        mapa_dias = {
            0: "Seg",
            1: "Ter",
            2: "Qua",
            3: "Qui",
            4: "Sex",
            5: "Sáb",
            6: "Dom",
        }
        receita_semana = df.groupby("dia_semana")["receita"].sum()
        labels = [mapa_dias.get(i, str(i)) for i in range(7)]
        valores = [receita_semana.get(i, 0) for i in range(7)]

        plt.figure()
        plt.bar(labels, valores)
        plt.title("Receita por Dia da Semana")
        plt.xlabel("Dia da semana")
        plt.ylabel("Receita (R$)")
        return self._salvar_figura("receita_dia_semana.png")

    def grafico_top_produtos(self, df: pd.DataFrame, n: int = 10) -> Path:
        """Top N produtos por receita (barra horizontal)."""
        top = (
            df.groupby("produto")["receita"]
            .sum()
            .nlargest(n)
            .sort_values(ascending=True)
        )

        plt.figure()
        plt.barh(top.index, top.values)
        plt.title(f"Top {n} Produtos por Receita")
        plt.xlabel("Receita (R$)")
        plt.ylabel("Produto")
        return self._salvar_figura("top_produtos.png")

    def grafico_distribuicao_ticket(self, df: pd.DataFrame) -> Path:
        """Boxplot do valor por transação (receita por linha)."""
        plt.figure()
        plt.boxplot(df["receita"], vert=False)
        plt.title("Distribuição da Receita por Transação")
        plt.xlabel("Receita por transação (R$)")
        return self._salvar_figura("distribuicao_ticket.png")

    def grafico_distribuicao_ticket_seaborn(self, df: pd.DataFrame) -> Path:
        """Distribuição do ticket com histograma + KDE em estilo premium."""
        import seaborn as sns

        plt.figure(figsize=(12, 6))
        sns.set_theme(style="darkgrid")

        ax = sns.histplot(
            df["receita"], 
            bins=30, 
            kde=True,
            stat="density",
            alpha=0.85
        )

        ax.set_title("Distribuição da Receita por Transação (Seaborn)", fontsize=14, fontweight="bold")
        ax.set_xlabel("Receita por transação (R$)")
        ax.set_ylabel("Densidade Estimada")

        return self._salvar_figura("ticket_distribuicao_seaborn.png")


    def grafico_heatmap_mes_semana(self, df: pd.DataFrame) -> Optional[Path]:
        """
        Heatmap simples: receita por mês (coluna) x dia da semana (linha).
        Se tiver poucos meses, ainda assim gera.
        """
        try:
            import numpy as np  # usado só aqui
        except ImportError:
            return None

        tabela = df.pivot_table(
            values="receita",
            index="dia_semana",
            columns="mes",
            aggfunc="sum",
            fill_value=0,
        )

        if tabela.empty:
            return None

        plt.figure()
        plt.imshow(tabela.values, aspect="auto")
        plt.colorbar(label="Receita (R$)")
        plt.title("Heatmap: Receita por Dia da Semana x Mês")
        plt.xlabel("Mês")
        plt.ylabel("Dia da semana")

        # Eixos
        plt.xticks(
            range(len(tabela.columns)),
            [f"{int(m):02d}" for m in tabela.columns],
        )
        mapa_dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        plt.yticks(
            range(len(tabela.index)),
            [mapa_dias[int(d)] for d in tabela.index],
        )

        return self._salvar_figura("heatmap_mes_semana.png")

    # ------------------------------------------------------------------ #
    # Função de conveniência para gerar tudo
    # ------------------------------------------------------------------ #

    def gerar_todos(self, df: pd.DataFrame) -> dict:
        """
        Gera todos os gráficos principais e devolve um dicionário
        com os caminhos relativos para uso no relatório HTML.
        """
        caminhos = {}
        caminhos["receita_diaria"] = self.grafico_receita_diaria(df)
        caminhos["receita_mensal"] = self.grafico_receita_mensal(df)
        caminhos["receita_dia_semana"] = self.grafico_receita_por_dia_semana(df)
        caminhos["top_produtos"] = self.grafico_top_produtos(df)
        caminhos["distribuicao_ticket"] = self.grafico_distribuicao_ticket(df)
        caminhos["distribuicao_ticket_seaborn"] = self.grafico_distribuicao_ticket_seaborn(df)
        heatmap = self.grafico_heatmap_mes_semana(df)
        if heatmap is not None:
            caminhos["heatmap_mes_semana"] = heatmap

        # Transformar para caminhos relativos a partir da pasta output
        caminhos_relativos = {
            chave: f"graficos/{Path(caminho).name}"
            for chave, caminho in caminhos.items()
        }
        return caminhos_relativos
