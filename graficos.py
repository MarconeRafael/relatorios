import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def gerar_graficos(caminho_csv):
    """Gera gráficos a partir dos dados do arquivo CSV."""
    try:
        # Lê os dados do CSV
        dados = pd.read_csv(caminho_csv)

        # Cria o diretório para os gráficos se não existir
        diretorio_graficos = 'data/graficos'
        os.makedirs(diretorio_graficos, exist_ok=True)

        # Preparar os dados para o gráfico
        dados_melted = dados.melt(id_vars='Etapa', 
                                   value_vars=['Tempo Gasto (min)', 'Tempo Esperado (min)', 'Diferença de Tempo'],
                                   var_name='Tipo', 
                                   value_name='Valor')

        # Gráfico: Comparação entre Tempo Gasto, Tempo Esperado e Diferença
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Etapa', y='Valor', hue='Tipo', data=dados_melted, palette='viridis')
        plt.title('Comparação de Tempo Gasto, Tempo Esperado e Diferença por Etapa')
        plt.xticks(rotation=45)
        plt.ylabel('Tempo (min)')
        plt.xlabel('Etapa')
        plt.legend(title='Tipo')
        plt.tight_layout()
        plt.savefig(f'{diretorio_graficos}/comparacao_tempos.png')  # Salva o gráfico
        plt.show()  # Mostra o gráfico

    except Exception as e:
        print(f"❌ Erro ao gerar gráficos: {e}")

if __name__ == "__main__":
    caminho_csv = 'data/relatorios/relatorio_eficiencia.csv'
    gerar_graficos(caminho_csv)
