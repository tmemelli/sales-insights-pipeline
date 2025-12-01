"""
Script: Gerador de Categorias de Produtos
Infere categorias e margens automaticamente a partir dos produtos únicos.

Uso:
    python scripts/gerar_categorias.py
"""

import pandas as pd
import re
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para imports funcionarem
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dados.carregador import CarregadorDados
from processamento.limpeza import LimpezaDados


class CategoriaInferidor:
    """
    Infere categorias de produtos baseado em palavras-chave
    e atribui margens estimadas por categoria.
    """
    
    def __init__(self):
        # IMPORTANTE: Ordem importa! Palavras mais específicas PRIMEIRO
        self.regras = {
            "notebook": "Notebook",
            "monitor": "Monitor",
            "teclado": "Teclado",
            "headset": "Headset",
            "fone|earphone": "Headset",
            "mousepad": "Mousepad",
            "mouse": "Mouse",
            "webcam|camera": "Webcam",  # ← Webcam ANTES de HD!
            "ssd": "Armazenamento",
            "\\bhd\\b": "Armazenamento",  # ← Só HD isolado (não em "Webcam HD")
            "memória|ram|ddr": "Memória RAM"
        }

        self.margens_padrao = {
            "Notebook": 0.20,
            "Monitor": 0.20,
            "Memória RAM": 0.25,
            "Mouse": 0.35,
            "Teclado": 0.35,
            "Headset": 0.30,
            "Armazenamento": 0.25,
            "Webcam": 0.30,
            "Mousepad": 0.40,
            "Outros": 0.22
        }

    def inferir_categoria(self, produto: str) -> str:
        """Classifica um produto em uma categoria baseada em palavras-chave."""
        produto_lower = produto.lower()
        for padrao, categoria in self.regras.items():
            if re.search(padrao, produto_lower):
                return categoria
        return "Outros"

    def gerar_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gera arquivo CSV com categorias e margens sugeridas.
        
        Args:
            df: DataFrame com coluna 'produto'
        
        Returns:
            DataFrame com categorias inferidas
        """
        produtos_unicos = df['produto'].unique()
        registros = []
        
        for produto in produtos_unicos:
            categoria = self.inferir_categoria(produto)
            margem = self.margens_padrao.get(categoria, 0.22)
            registros.append([produto, categoria, margem])

        df_cat = pd.DataFrame(
            registros, 
            columns=["produto", "categoria_sugerida", "margem_sugerida"]
        )

        # Salva na pasta dados/
        pasta_dados = BASE_DIR / "dados"
        pasta_dados.mkdir(exist_ok=True)
        
        caminho = pasta_dados / "categorias_produtos.csv"
        df_cat.to_csv(caminho, index=False, encoding="utf-8")

        print(f"\n✅ Arquivo gerado: {caminho}")
        print(f"📦 {len(produtos_unicos)} produtos categorizados!")
        print(f"\n📊 Distribuição de categorias:")
        print(df_cat['categoria_sugerida'].value_counts())

        return df_cat


if __name__ == "__main__":
    print("="*70)
    print("🏷️  GERADOR DE CATEGORIAS DE PRODUTOS")
    print("="*70 + "\n")
    
    # Caminho para o CSV de vendas
    caminho_csv = BASE_DIR / "dados" / "dados_vendas.csv"
    
    # Carrega dados
    loader = CarregadorDados(str(caminho_csv))
    df = loader.carregar()

    # Limpa (para pegar apenas produtos válidos)
    cleaner = LimpezaDados()
    df_limpo = cleaner.limpar(df)

    # Gera categorias
    inferidor = CategoriaInferidor()
    tabela = inferidor.gerar_csv(df_limpo)
    
    print("\n👀 Preview das categorias geradas:")
    print(tabela.head(10))
    
    print("\n✅ Processo concluído!")
    print("📝 Edite 'dados/categorias_produtos.csv' se precisar ajustar as categorias.\n")