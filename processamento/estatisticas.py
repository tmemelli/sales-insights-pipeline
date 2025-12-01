"""
Módulo: Estatísticas de Vendas
Responsável por calcular KPIs financeiros, de produtos e sazonalidade
a partir dos dados já limpos.

Versão: 2.0 (Estrutura padronizada e achatada)
"""

import pandas as pd
from typing import Dict, Any, List, Tuple


class EstatisticasVendas:
    """
    Classe responsável pelo cálculo das principais estatísticas de vendas.

    Requisitos do DataFrame de entrada (já limpo):
    - colunas obrigatórias:
        ['data', 'produto', 'valor', 'quantidade', 'receita',
         'ano', 'mes', 'dia_semana']
    - 'data' em datetime64[ns]
    - 'receita' = valor * quantidade
    """

    # Margens estimadas por "categoria" baseada no nome do produto
    MARGENS_CATEGORIA = {
        "notebook": 0.10,
        "monitor": 0.15,
        "ssd": 0.25,
        "hd": 0.20,
        "memória": 0.30,
        "memoria": 0.30,
        "ram": 0.30,
        "mouse": 0.50,
        "teclado": 0.45,
        "headset": 0.40,
        "fone": 0.40,
        "webcam": 0.35,
        "cadeira": 0.30,
        "mousepad": 0.60,
    }

    MARGEM_PADRAO = 0.25

    def __init__(self) -> None:
        self.resultados: Dict[str, Any] = {}

    # ============================================================
    # Helpers internos
    # ============================================================

    def _fmt(self, valor: float, casas: int = 2) -> float:
        """Formata valores numéricos com casas decimais fixas."""
        return round(float(valor), casas)

    def _validar_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Garante que o DataFrame tenha as colunas mínimas e tipos adequados."""
        colunas_necessarias = {
            "data", "produto", "valor", "quantidade", 
            "receita", "ano", "mes", "dia_semana"
        }

        faltando = colunas_necessarias - set(df.columns)
        if faltando:
            raise ValueError(f"❌ DataFrame incompleto. Colunas faltando: {faltando}")

        df = df.copy()

        if not pd.api.types.is_datetime64_any_dtype(df["data"]):
            df["data"] = pd.to_datetime(df["data"], errors="coerce")

        if df["data"].isna().any():
            df = df[df["data"].notna()].copy()

        return df

    def _margem_produto(self, nome_produto: str) -> float:
        """Retorna a margem estimada para um produto."""
        nome = str(nome_produto).lower()
        for palavra, margem in self.MARGENS_CATEGORIA.items():
            if palavra in nome:
                return margem
        return self.MARGEM_PADRAO

    # ============================================================
    # Cálculos de Estatísticas
    # ============================================================

    def calcular(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Ponto de entrada principal.
        Retorna dicionário ACHATADO com todas as estatísticas.
        """
        if df.empty:
            raise ValueError("DataFrame vazio recebido em EstatisticasVendas.calcular()")

        df = self._validar_dataframe(df)

        # ==================== FINANCEIRO ====================
        receita_total = df["receita"].sum()
        total_transacoes = len(df)
        total_unidades = df["quantidade"].sum()

        ticket_medio = self._fmt(
            receita_total / total_transacoes if total_transacoes > 0 else 0
        )

        receita_por_dia = df.groupby("data")["receita"].sum()
        receita_media_diaria = self._fmt(
            receita_por_dia.mean() if not receita_por_dia.empty else 0
        )

        data_inicio = df["data"].min()
        data_fim = df["data"].max()
        dias_analisados = (data_fim - data_inicio).days + 1 if not df.empty else 0

        # Lucro estimado
        margens = df["produto"].apply(self._margem_produto)
        lucro_estimado = (df["receita"] * margens).sum()
        margem_media = lucro_estimado / receita_total if receita_total > 0 else 0

        # ==================== PRODUTOS ====================
        receita_por_produto = (
            df.groupby("produto")["receita"]
            .sum()
            .sort_values(ascending=False)
        )

        unidades_por_produto = (
            df.groupby("produto")["quantidade"]
            .sum()
            .sort_values(ascending=False)
        )

        # Top produtos como LISTA DE TUPLAS (para HTML)
        top_produtos: List[Tuple[str, float]] = [
            (produto, self._fmt(valor))
            for produto, valor in receita_por_produto.head(10).items()
        ]

        # Curva ABC
        curva = receita_por_produto.reset_index()
        curva.columns = ["produto", "receita"]
        curva["receita"] = curva["receita"].astype(float)
        curva["participacao_percent"] = (
            curva["receita"] / receita_total * 100 if receita_total > 0 else 0
        )
        curva["participacao_acumulada"] = curva["participacao_percent"].cumsum()

        def classifica_abc(valor_acumulado: float) -> str:
            if valor_acumulado <= 80:
                return "A"
            elif valor_acumulado <= 95:
                return "B"
            return "C"

        curva["classe_abc"] = curva["participacao_acumulada"].apply(classifica_abc)

        # Curva ABC como LISTA DE TUPLAS (produto, receita, classe)
        curva_abc: List[Tuple[str, float, str]] = [
            (row["produto"], self._fmt(row["receita"]), row["classe_abc"])
            for _, row in curva.head(10).iterrows()
        ]

        # ==================== SAZONALIDADE ====================
        mapa_dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

        receita_por_dia_semana = (
            df.groupby("dia_semana")["receita"]
            .sum()
            .reindex(range(7), fill_value=0)
        )

        melhor_dia_idx = receita_por_dia_semana.idxmax()
        melhor_dia_nome = mapa_dias[melhor_dia_idx]

        receita_dia_semana: Dict[str, float] = {
            mapa_dias[i]: self._fmt(valor)
            for i, valor in receita_por_dia_semana.items()
        }

        # Receita mensal
        receita_mensal_group = (
            df.groupby(["ano", "mes"])["receita"]
            .sum()
            .sort_index()
        )

        receita_mensal: Dict[str, float] = {}
        for (ano, mes), valor in receita_mensal_group.items():
            chave = f"{ano}-{mes:02d}"
            receita_mensal[chave] = self._fmt(valor)

        # Crescimento
        if len(receita_mensal_group) >= 2:
            primeiro = receita_mensal_group.iloc[0]
            ultimo = receita_mensal_group.iloc[-1]
            crescimento = (ultimo - primeiro) / primeiro * 100 if primeiro > 0 else 0
        else:
            crescimento = 0.0

        # Melhor/pior mês
        if not receita_mensal_group.empty:
            idx_melhor = receita_mensal_group.idxmax()
            idx_pior = receita_mensal_group.idxmin()
            melhor_mes = f"{idx_melhor[0]}-{idx_melhor[1]:02d}"
            pior_mes = f"{idx_pior[0]}-{idx_pior[1]:02d}"
        else:
            melhor_mes = None
            pior_mes = None

        # Top 10 dias
        receita_por_dia_full = (
            df.groupby("data")["receita"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        top_dias: List[Tuple[str, float]] = [
            (data.strftime("%d/%m/%Y"), self._fmt(valor))
            for data, valor in receita_por_dia_full.items()
        ]

        # ==================== QUALIDADE TEMPORAL ====================
        dias_periodo = dias_analisados
        dias_com_venda = df["data"].nunique()
        densidade = (dias_com_venda / dias_periodo * 100) if dias_periodo > 0 else 0.0

        # ==================== RESULTADO ACHATADO ====================
        self.resultados = {
            # Financeiro
            "gmv": self._fmt(receita_total),
            "lucro_estimado": self._fmt(lucro_estimado),
            "margem_media_percent": self._fmt(margem_media * 100),
            "total_transacoes": int(total_transacoes),
            "total_unidades": int(total_unidades),
            "ticket_medio": ticket_medio,
            "receita_media_diaria": receita_media_diaria,
            "data_inicio": data_inicio.strftime("%d/%m/%Y") if pd.notna(data_inicio) else None,
            "data_fim": data_fim.strftime("%d/%m/%Y") if pd.notna(data_fim) else None,
            "dias_analisados": int(dias_analisados),
            
            # Produtos
            "top_produtos": top_produtos,  # Lista de tuplas
            "curva_abc": curva_abc,  # Lista de tuplas
            
            # Sazonalidade
            "receita_dia_semana": receita_dia_semana,
            "melhor_dia_semana": melhor_dia_nome,
            "receita_mensal": receita_mensal,
            "crescimento_percentual": self._fmt(crescimento),
            "melhor_mes": melhor_mes,
            "pior_mes": pior_mes,
            "top_dias": top_dias,  # Lista de tuplas
            
            # Qualidade
            "dias_com_venda": int(dias_com_venda),
            "dias_periodo": int(dias_periodo),
            "densidade_temporal_percent": self._fmt(densidade),
        }

        return self.resultados

    def get_resultados(self) -> Dict[str, Any]:
        """Retorna o último cálculo de estatísticas."""
        return self.resultados