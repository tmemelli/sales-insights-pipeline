"""
Módulo: Insights Automáticos
Gera mensagens inteligentes baseadas nas estatísticas e tendências encontradas.

Versão: 2.0 (Adaptado para estrutura achatada)
"""

import pandas as pd
from typing import Dict, Any


class InsightsVendas:
    """
    Classe responsável por gerar insights automáticos a partir das estatísticas.
    """

    def gerar(self, df: pd.DataFrame, estatisticas: Dict[str, Any]) -> Dict[str, str]:
        """
        Gera insights automáticos baseados nos dados e estatísticas.
        
        Args:
            df: DataFrame limpo (usado se precisar calcular algo extra)
            estatisticas: Dicionário com estatísticas (estrutura achatada)
        
        Returns:
            Dicionário com insights {chave: mensagem_html}
        """
        insights = {}

        # ========== INSIGHT 1: Produto Campeão ==========
        top_produtos = estatisticas.get("top_produtos", [])
        if top_produtos:
            nome, receita = top_produtos[0]
            receita_total = estatisticas.get("gmv", 0)
            
            if receita_total > 0:
                participacao = (receita / receita_total) * 100
                insights["produto_campeao"] = (
                    f"🏆 <strong>{nome}</strong> é o produto campeão, "
                    f"gerando <strong>R$ {receita:,.2f}</strong> "
                    f"({participacao:.1f}% do faturamento total)."
                )
            else:
                insights["produto_campeao"] = (
                    f"🏆 <strong>{nome}</strong> é o produto campeão, "
                    f"gerando <strong>R$ {receita:,.2f}</strong>."
                )

        # ========== INSIGHT 2: Melhor Dia da Semana ==========
        melhor_dia = estatisticas.get("melhor_dia_semana")
        receita_dia_semana = estatisticas.get("receita_dia_semana", {})
        
        if melhor_dia and receita_dia_semana:
            receita_melhor = receita_dia_semana.get(melhor_dia, 0)
            insights["melhor_dia_semana"] = (
                f"📅 <strong>{melhor_dia}</strong> é o melhor dia para vendas, "
                f"com <strong>R$ {receita_melhor:,.2f}</strong> em receita acumulada."
            )

        # ========== INSIGHT 3: Melhor Mês ==========
        melhor_mes = estatisticas.get("melhor_mes")
        receita_mensal = estatisticas.get("receita_mensal", {})
        
        if melhor_mes and melhor_mes in receita_mensal:
            receita_mes = receita_mensal[melhor_mes]
            # Formatar mês (2024-01 -> Jan/2024)
            ano, mes = melhor_mes.split("-")
            meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
                    "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            mes_nome = meses[int(mes) - 1]
            
            insights["melhor_mes"] = (
                f"📆 O melhor mês foi <strong>{mes_nome}/{ano}</strong>, "
                f"com <strong>R$ {receita_mes:,.2f}</strong> em faturamento."
            )

        # ========== INSIGHT 4: Crescimento ==========
        crescimento = estatisticas.get("crescimento_percentual", 0)
        
        if crescimento > 5:
            insights["crescimento"] = (
                f"📈 Crescimento positivo de <strong>{crescimento:.1f}%</strong> "
                f"no período analisado!"
            )
        elif crescimento < -5:
            insights["queda"] = (
                f"📉 Atenção: queda de <strong>{abs(crescimento):.1f}%</strong> "
                f"no período. Recomenda-se análise detalhada."
            )
        else:
            insights["estabilidade"] = (
                f"➡️ Vendas estáveis, com variação de <strong>{crescimento:.1f}%</strong>."
            )

        # ========== INSIGHT 5: Concentração (Curva ABC) ==========
        curva_abc = estatisticas.get("curva_abc", [])
        gmv = estatisticas.get("gmv", 0)
        
        if curva_abc and gmv > 0:
            # Soma receita dos produtos classe A
            receita_a = sum(receita for _, receita, classe in curva_abc if classe == "A")
            concentracao = (receita_a / gmv) * 100
            
            produtos_a = len([p for p, r, c in curva_abc if c == "A"])
            
            insights["concentracao"] = (
                f"📊 <strong>{produtos_a} produtos</strong> da classe A representam "
                f"<strong>{concentracao:.1f}%</strong> da receita total."
            )

        # ========== INSIGHT 6: Qualidade Temporal ==========
        densidade = estatisticas.get("densidade_temporal_percent", 0)
        
        if densidade > 95:
            insights["qualidade_excelente"] = (
                f"✅ Excelente densidade de dados (<strong>{densidade:.1f}%</strong>), "
                f"cobrindo praticamente todo o período analisado."
            )
        elif densidade > 80:
            insights["qualidade_boa"] = (
                f"✔️ Boa presença de dados ao longo do período "
                f"(<strong>{densidade:.1f}%</strong> de cobertura)."
            )
        elif densidade > 60:
            insights["qualidade_media"] = (
                f"⚠️ Cobertura mediana de dados (<strong>{densidade:.1f}%</strong>). "
                f"Algumas lacunas podem afetar análises de tendência."
            )
        else:
            insights["qualidade_baixa"] = (
                f"⚠️ Baixa densidade de dados (<strong>{densidade:.1f}%</strong>). "
                f"Existem lacunas significativas que podem distorcer conclusões."
            )

        # ========== INSIGHT 7: Dia de Pico ==========
        top_dias = estatisticas.get("top_dias", [])
        
        if top_dias:
            data_pico, valor_pico = top_dias[0]
            insights["dia_pico"] = (
                f"🔥 Dia com maior receita: <strong>{data_pico}</strong>, "
                f"com <strong>R$ {valor_pico:,.2f}</strong> em faturamento."
            )

        # ========== INSIGHT 8: Ticket Médio ==========
        ticket_medio = estatisticas.get("ticket_medio", 0)
        
        if ticket_medio > 0:
            if ticket_medio > 500:
                insights["ticket_alto"] = (
                    f"💰 Ticket médio alto de <strong>R$ {ticket_medio:,.2f}</strong> "
                    f"indica vendas de produtos premium."
                )
            elif ticket_medio > 200:
                insights["ticket_medio"] = (
                    f"💵 Ticket médio de <strong>R$ {ticket_medio:,.2f}</strong> "
                    f"está em patamar saudável."
                )
            else:
                insights["ticket_baixo"] = (
                    f"💸 Ticket médio de <strong>R$ {ticket_medio:,.2f}</strong>. "
                    f"Considere estratégias de upsell."
                )

        return insights


# ============================================================================
# EXEMPLO DE USO (para testes)
# ============================================================================
if __name__ == "__main__":
    # Exemplo de estatísticas mockadas
    stats_exemplo = {
        "gmv": 100000,
        "top_produtos": [("Notebook Dell", 45000), ("Monitor LG", 25000)],
        "melhor_dia_semana": "Sex",
        "receita_dia_semana": {"Sex": 25000, "Seg": 15000},
        "melhor_mes": "2024-06",
        "receita_mensal": {"2024-06": 35000, "2024-07": 30000},
        "crescimento_percentual": 15.5,
        "densidade_temporal_percent": 87.3,
        "top_dias": [("15/06/2024", 8500), ("22/06/2024", 7200)],
        "ticket_medio": 325.50,
        "curva_abc": [
            ("Notebook Dell", 45000, "A"),
            ("Monitor LG", 25000, "A"),
            ("Mouse", 5000, "B")
        ]
    }
    
    gerador = InsightsVendas()
    insights = gerador.gerar(pd.DataFrame(), stats_exemplo)
    
    print("🎯 INSIGHTS GERADOS:\n")
    for chave, texto in insights.items():
        print(f"• {texto}\n")