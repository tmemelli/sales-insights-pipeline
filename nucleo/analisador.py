"""
Módulo: Analisador de Vendas
Orquestra todo o pipeline de análise.

Versão: 2.0 (Com path relativo inteligente)
"""

from pathlib import Path
from dados.carregador import CarregadorDados
from processamento.limpeza import LimpezaDados
from processamento.estatisticas import EstatisticasVendas
from analise.insights import InsightsVendas
from visualizacao.graficos import GraficosVendas
from relatorio.gerador_html import GeradorRelatorioHTML


class AnalisadorVendas:
    """
    Classe que orquestra todo o pipeline de análise de vendas.
    """

    def __init__(self, caminho_csv: str = None):
        """
        Inicializa o analisador.
        
        Args:
            caminho_csv: Caminho para o arquivo CSV.
                        Se None, usa dados/dados_vendas.csv automaticamente.
        """
        if caminho_csv is None:
            # Encontra a pasta raiz do projeto (onde está este arquivo)
            base_dir = Path(__file__).resolve().parent.parent
            caminho_csv = str(base_dir / "dados" / "dados_vendas.csv")
        
        self.caminho_csv = caminho_csv

    def executar(self):
        """Executa o pipeline completo de análise."""
        print("\n" + "="*70)
        print("🚀 ANALISADOR DE VENDAS - PIPELINE COMPLETO")
        print("="*70 + "\n")

        # 1) Carregar
        loader = CarregadorDados(self.caminho_csv)
        df = loader.carregar()

        # 2) Limpar
        cleaner = LimpezaDados()
        df_limpo = cleaner.limpar(df)

        # 3) Estatísticas
        print("\n📊 Calculando estatísticas...")
        calc_stats = EstatisticasVendas()
        estatisticas = calc_stats.calcular(df_limpo)
        print("✅ Estatísticas calculadas!")

        # 4) Insights automáticos
        print("\n💡 Gerando insights automáticos...")
        gerador_insights = InsightsVendas()
        insights = gerador_insights.gerar(df_limpo, estatisticas)
        print(f"✅ {len(insights)} insights gerados!")

        # 5) Gráficos
        print("\n📈 Gerando visualizações...")
        graficos = GraficosVendas()
        caminhos_graficos = graficos.gerar_todos(df_limpo)
        print(f"✅ {len(caminhos_graficos)} gráficos criados!")

        # 6) Relatório HTML
        print("\n📄 Gerando relatório HTML...")
        gerador_relatorio = GeradorRelatorioHTML()
        gerador_relatorio.gerar(df_limpo, estatisticas, insights, caminhos_graficos)

        print("\n" + "="*70)
        print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print("\n📂 Arquivos gerados:")
        print("   • output/relatorio_vendas.html")
        print("   • output/graficos/*.png")
        print("\n💡 Próximo passo: Abra o relatório HTML no navegador!\n")

        return df_limpo, estatisticas, insights