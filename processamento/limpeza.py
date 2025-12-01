"""
Módulo: Limpeza e Validação de Dados
Responsável por transformar os dados brutos em dados utilizáveis.
Aplica validações e cria novas colunas úteis.

Versão: 2.1 (Refatorada com melhorias)
"""

import pandas as pd
from typing import Dict, Any


class LimpezaDados:
    """
    Classe responsável pela limpeza e validação de dados de vendas.

    Melhorias aplicadas:
    - Relatório detalhado de limpeza
    - Remoção de outliers extremos com limite configurável
    - Código mais DRY
    - Evita SettingWithCopyWarning
    - Prints padronizados
    """

    COLUNAS_OBRIGATORIAS = ["data", "produto", "valor", "quantidade"]

    def __init__(self):
        self.relatorio: Dict[str, Any] = {}

    # -------------------------------------------------------------
    def validar_colunas(self, df: pd.DataFrame) -> None:
        faltando = [col for col in self.COLUNAS_OBRIGATORIAS if col not in df.columns]
        if faltando:
            raise ValueError(
                f"❌ Colunas ausentes: {faltando}\n📋 Colunas disponíveis: {list(df.columns)}"
            )

    # -------------------------------------------------------------
    def remover_duplicatas(self, df: pd.DataFrame) -> pd.DataFrame:
        antes = len(df)
        df = df.drop_duplicates()
        removidas = antes - len(df)
        self.relatorio["duplicatas_removidas"] = removidas

        if removidas > 0:
            print(f"   🗑️ {removidas} duplicatas removidas")

        return df

    # -------------------------------------------------------------
    def converter_tipos(self, df: pd.DataFrame) -> pd.DataFrame:
        conversoes = {
            "data": lambda x: pd.to_datetime(x, errors="coerce"),
            "valor": lambda x: pd.to_numeric(x, errors="coerce"),
            "quantidade": lambda x: pd.to_numeric(x, errors="coerce"),
        }

        invalidos_total = 0

        for coluna, funcao in conversoes.items():
            if coluna in df.columns:
                antes = df[coluna].notna().sum()
                df[coluna] = funcao(df[coluna])
                depois = df[coluna].notna().sum()
                invalidos = antes - depois
                invalidos_total += invalidos

                if invalidos > 0:
                    print(f"   ⚠️ {invalidos} valores convertidos para NaN em '{coluna}'")

        self.relatorio["valores_invalidos_convertidos"] = invalidos_total
        return df

    # -------------------------------------------------------------
    def remover_registros_invalidos(self, df: pd.DataFrame) -> pd.DataFrame:
        antes = len(df)

        df = df.dropna(subset=self.COLUNAS_OBRIGATORIAS)
        df = df[(df["valor"] > 0) & (df["quantidade"] > 0)]

        df["valor"] = df["valor"].astype(float)
        df["quantidade"] = df["quantidade"].astype(int)

        removidos = antes - len(df)
        self.relatorio["registros_invalidos"] = removidos

        if removidos > 0:
            print(f"   🧹 {removidos} registros inválidos removidos")

        return df

    # -------------------------------------------------------------
    def remover_outliers_extremos(
        self, df: pd.DataFrame, coluna: str = "valor", limite_iqr: int = 3
    ) -> pd.DataFrame:

        if coluna not in df.columns:
            return df

        antes = len(df)

        Q1 = df[coluna].quantile(0.25)
        Q3 = df[coluna].quantile(0.75)
        IQR = Q3 - Q1

        limite_inferior = Q1 - limite_iqr * IQR
        limite_superior = Q3 + limite_iqr * IQR

        df = df[(df[coluna] >= limite_inferior) & (df[coluna] <= limite_superior)]

        removidos = antes - len(df)
        self.relatorio["outliers_removidos_valor"] = removidos

        if removidos > 0:
            print(f"   📊 {removidos} outliers extremos removidos de '{coluna}'")

        return df

    # -------------------------------------------------------------
    def criar_features_derivadas(self, df: pd.DataFrame) -> pd.DataFrame:
        df["receita"] = df["valor"] * df["quantidade"]
        df["ano"] = df["data"].dt.year
        df["mes"] = df["data"].dt.month
        df["dia_semana"] = df["data"].dt.dayofweek
        df["dia_mes"] = df["data"].dt.day
        df["semana_ano"] = df["data"].dt.isocalendar().week

        print("   ✨ Features derivadas criadas")
        return df

    # -------------------------------------------------------------
    def aplicar_categorias(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Integra categorias e margens ao DataFrame limpo,
        adicionando colunas: categoria, margem e lucro.
        """
        try:
            categorias = pd.read_csv("dados/categorias_produtos.csv")
        except FileNotFoundError:
            print("⚠️ Arquivo de categorias não encontrado! Ignorando categorização...")
            df["categoria"] = "Outros"
            df["margem"] = 0.20  # margem genérica
            df["lucro"] = (df["receita"] * df["margem"]).round(2)
            return df

        # Merge
        df = df.merge(categorias, on="produto", how="left")

        # Contar produtos não encontrados no CSV
        sem_cat = df["categoria_sugerida"].isna().sum()
        if sem_cat > 0:
            print(f"⚠️ {sem_cat} produtos sem categoria → aplicando 'Outros'")

        # Ajustar campos finais
        df["categoria"] = df["categoria_sugerida"].fillna("Outros")
        df["margem"] = df["margem_sugerida"].fillna(0.20)
        df["lucro"] = (df["receita"] * df["margem"]).round(2)

        # Remover colunas auxiliares
        df = df.drop(columns=["categoria_sugerida", "margem_sugerida"])

        # Atualizar relatório
        self.relatorio["produtos_sem_categoria"] = sem_cat

        return df

    # -------------------------------------------------------------
    def ordenar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values("data").reset_index(drop=True)
        print("   📅 Dados ordenados cronologicamente")
        return df

    # -------------------------------------------------------------
    def limpar(self, df: pd.DataFrame) -> pd.DataFrame:
        print("\n🧹 Limpando e validando dados...")

        df = df.copy()  # *Uma vez só*
        inicial = len(df)
        self.relatorio["registros_iniciais"] = inicial

        # Pipeline
        self.validar_colunas(df)
        df = self.remover_duplicatas(df)
        df = self.converter_tipos(df)
        df = self.remover_registros_invalidos(df)
        df = self.remover_outliers_extremos(df, "valor", limite_iqr=3)
        df = self.criar_features_derivadas(df)
        df = self.aplicar_categorias(df)
        df = self.ordenar_dados(df)

        final = len(df)
        self.relatorio["registros_finais"] = final
        self.relatorio["taxa_aproveitamento"] = round((final / inicial) * 100, 2)

        print(f"\n✅ Limpeza concluída:")
        print(f"   📉 Registros removidos: {inicial-final} ({self.relatorio['taxa_aproveitamento']}% aproveitamento)")
        print(f"   📈 Registros finais limpos: {final}")

        return df

    # -------------------------------------------------------------
    def get_relatorio(self) -> Dict[str, Any]:
        return self.relatorio
