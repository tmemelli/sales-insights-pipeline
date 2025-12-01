"""
Módulo: Carregador de Dados
Responsável por ler o arquivo CSV e devolver um DataFrame.
Segue o princípio da responsabilidade única (SRP).
"""

import pandas as pd
from pathlib import Path


class CarregadorDados:
    """
    Classe responsável por carregar dados de arquivos CSV.
    
    Melhorias:
    - Validação separada do carregamento (SRP)
    - Mais testável
    - Mais reutilizável
    """

    def __init__(self, caminho_arquivo: str):
        """
        Inicializa o carregador com o caminho do arquivo
        
        Args:
            caminho_arquivo: Caminho para o arquivo CSV
        """
        self.caminho_arquivo = Path(caminho_arquivo)

    def validar_arquivo(self) -> bool:
        """
        Valida se o arquivo existe e pode ser lido
        
        Returns:
            True se arquivo válido, False caso contrário
        """
        # Verifica se o arquivo existe
        if not self.caminho_arquivo.exists():
            print(f"❌ Arquivo não encontrado: {self.caminho_arquivo}")
            return False
        
        # Verifica se é um arquivo (não pasta)
        if not self.caminho_arquivo.is_file():
            print(f"❌ O caminho não é um arquivo: {self.caminho_arquivo}")
            return False
        
        # Aviso se não for CSV (mas não bloqueia)
        if self.caminho_arquivo.suffix.lower() != '.csv':
            print(f"⚠️ Aviso: arquivo não tem extensão .csv ({self.caminho_arquivo.suffix})")
            print(f"   Vou tentar carregar mesmo assim...")
        
        return True

    def carregar(self) -> pd.DataFrame:
        """
        Carrega dados do arquivo CSV
        
        Returns:
            DataFrame com os dados carregados
        
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se houver erro ao ler o CSV ou arquivo vazio
        """
        print("📂 Carregando dados...")

        # Valida ANTES de tentar carregar
        if not self.validar_arquivo():
            raise FileNotFoundError(
                f"Arquivo inválido ou não encontrado: {self.caminho_arquivo}"
            )
        
        # Tenta carregar o CSV
        try:
            df = pd.read_csv(self.caminho_arquivo)
        except pd.errors.EmptyDataError:
            raise ValueError("❌ O arquivo CSV está vazio!")
        except pd.errors.ParserError as e:
            raise ValueError(f"❌ Erro ao processar o CSV: {e}")
        except UnicodeDecodeError:
            # Tenta com encoding alternativo
            print("⚠️ Erro de encoding UTF-8, tentando com latin-1...")
            try:
                df = pd.read_csv(self.caminho_arquivo, encoding='latin-1')
            except Exception as e:
                raise ValueError(f"❌ Erro definitivo ao ler o arquivo: {e}")
        except Exception as e:
            raise ValueError(f"❌ Erro inesperado ao carregar: {e}")
        
        # Verifica se o DataFrame está vazio
        if df.empty:
            raise ValueError("❌ O arquivo foi carregado, mas não contém dados!")
        
        print(f"✅ {len(df)} registros carregados com sucesso.")
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        
        return df
    
    def info_arquivo(self) -> dict:
        """
        Retorna informações sobre o arquivo (útil para debug)
        
        Returns:
            Dicionário com informações do arquivo
        """
        if not self.caminho_arquivo.exists():
            return {"status": "Arquivo não existe"}
        
        return {
            "nome": self.caminho_arquivo.name,
            "caminho_completo": str(self.caminho_arquivo.absolute()),
            "tamanho_kb": round(self.caminho_arquivo.stat().st_size / 1024, 2),
            "extensao": self.caminho_arquivo.suffix,
            "existe": self.caminho_arquivo.exists()
        }
