# 📊 Sales Insights Pipeline

> Sistema automatizado de análise de dados de vendas com geração de relatórios HTML profissionais.

## 🚀 Tecnologias

- Python 3.8+
- Pandas
- Matplotlib
- Seaborn

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/tmemelli/sales-insights-pipeline.git
cd sales-insights-pipeline

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
.\venv\Scripts\Activate   # Windows

# Instale as dependências
pip install -r requirements.txt
```

## 🎯 Como Usar

```bash
# 1. Gere as categorias (primeira vez)
python scripts/gerar_categorias.py

# 2. Execute a análise completa
python main.py

# 3. Abra o relatório
# Arquivo gerado: output/relatorio_vendas.html
```

## 📁 Estrutura

```
├── dados/              # Dados e carregamento
├── processamento/      # Limpeza e estatísticas
├── analise/           # Geração de insights
├── visualizacao/      # Criação de gráficos
├── relatorio/         # Geração de HTML
├── nucleo/            # Orquestração do pipeline
├── scripts/           # Scripts utilitários
├── output/            # Relatórios e gráficos gerados
└── main.py            # Ponto de entrada
```

## 👨‍💻 Autor

**Thiago Memelli**
- GitHub: [@tmemelli](https://github.com/tmemelli)

## 📄 Licença

MIT License

---

*Projeto em desenvolvimento - Documentação completa em breve*