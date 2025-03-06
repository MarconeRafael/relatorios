import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.lines as mlines
import numpy as np

def gerar_graficos_barras_tempo(caminho_csv):
    caminho_csv =  caminho_csv

    """Gera gráfico de barras com as colunas na ordem desejada e cores customizadas."""
    try:
        import os
        import pandas as pd
        import matplotlib.pyplot as plt
        import numpy as np

        # Lê os dados do CSV
        dados = pd.read_csv(caminho_csv)

        # Cria o diretório para os gráficos se não existir
        diretorio_graficos = 'data/graficos'
        os.makedirs(diretorio_graficos, exist_ok=True)

        # Configura a posição de cada grupo de barras
        n = len(dados)
        x = np.arange(n)
        width = 0.25

        fig, ax = plt.subplots(figsize=(12, 6))

        # Plota "Tempo Esperado (min)" na primeira coluna (posição x - width) com cor azul
        ax.bar(x - width, dados["Tempo Esperado (min)"], width,
               label='Tempo Esperado (min)', color='blue')

        # Plota "Tempo Gasto (min)" na segunda coluna (posição x) com cor preta
        ax.bar(x, dados["Tempo Gasto (min)"], width,
               label='Tempo Gasto (min)', color='black')

        # Define as cores para "Diferença de Tempo": vermelho se positivo, verde se negativo
        cores_diferenca = ['red' if v > 0 else 'green' for v in dados["Diferença de Tempo"]]
        # Plota "Diferença de Tempo" na terceira coluna (posição x + width)
        ax.bar(x + width, dados["Diferença de Tempo"], width,
               label='Diferença de Tempo', color=cores_diferenca)

        # Configurações do gráfico
        ax.set_title('Comparação de Tempo Gasto, Tempo Esperado e Diferença por Etapa')
        ax.set_ylabel('Tempo (min)')
        ax.set_xlabel('Etapa')
        ax.set_xticks(x)
        ax.set_xticklabels(dados["Etapa"], rotation=45)
        ax.legend(title='Tipo')

        plt.tight_layout()
        plt.savefig(f'{diretorio_graficos}/comparacao_tempos.png')  # Salva o gráfico
        plt.show()

    except Exception as e:
        print(f"❌ Erro ao gerar gráficos: {e}")




def gerar_graficos_pontos_tempo(caminho_csv):
    caminho_csv =  caminho_csv

    """Gera gráficos de linhas múltiplas a partir dos dados do CSV."""
    try:
        # Lê os dados do CSV
        dados = pd.read_csv(caminho_csv)

        # Assume que os dados possuem as colunas 'Etapa', 'Tempo Gasto (min)' e 'Tempo Esperado (min)'
        # Calcula a diferença: Tempo Gasto - Tempo Esperado
        dados['Diferença de Tempo'] = dados['Tempo Gasto (min)'] - dados['Tempo Esperado (min)']

        # Define o eixo x como índices numéricos e usa as labels de 'Etapa' para os ticks
        x = np.arange(len(dados))

        # Séries de dados
        tempo_esperado = dados['Tempo Esperado (min)']
        tempo_gasto = dados['Tempo Gasto (min)']
        diff = dados['Diferença de Tempo']

        # Cria a figura
        plt.figure(figsize=(12, 6))

        # Plota Tempo Esperado em azul
        plt.plot(x, tempo_esperado, color='blue', marker='o', linestyle='-', label='Tempo Esperado')

        # Plota Tempo Gasto em preto
        plt.plot(x, tempo_gasto, color='black', marker='o', linestyle='-', label='Tempo Gasto')

        # Função auxiliar para plotar a linha de Diferença com cores conforme o sinal
        def plot_diff_line(x, y):
            start = 0
            # Itera pelos pontos para identificar segmentos com sinal consistente
            for i in range(1, len(x)):
                if (y[i] >= 0) == (y[i-1] >= 0):
                    continue
                # Plota o segmento de start até i
                segment_x = x[start:i]
                segment_y = y[start:i]
                cor = 'red' if segment_y.iloc[0] >= 0 else 'green'
                plt.plot(segment_x, segment_y, color=cor, marker='o', linestyle='-')
                start = i
            # Plota o último segmento
            segment_x = x[start:]
            segment_y = y[start:]
            if not segment_y.empty:
                cor = 'red' if segment_y.iloc[0] >= 0 else 'green'
                plt.plot(segment_x, segment_y, color=cor, marker='o', linestyle='-')

        # Plota a linha de Diferença
        plot_diff_line(x, diff)

        # Configura os rótulos do eixo x com as etapas
        plt.xticks(x, dados['Etapa'], rotation=45)
        plt.xlabel('Etapa')
        plt.ylabel('Tempo (min) e Diferença')
        plt.title('Comparação: Tempo Esperado, Tempo Gasto e Diferença de Tempo')

        # Cria handles para a legenda das diferenças (apenas se houver pontos positivos ou negativos)
        handles, labels = plt.gca().get_legend_handles_labels()
        if any(diff >= 0):
            handles.append(mlines.Line2D([], [], color='red', marker='o', linestyle='-', label='Diferença (Positiva)'))
            labels.append('Diferença (Positiva)')
        if any(diff < 0):
            handles.append(mlines.Line2D([], [], color='green', marker='o', linestyle='-', label='Diferença (Negativa)'))
            labels.append('Diferença (Negativa)')
        plt.legend(handles=handles, labels=labels)

        plt.tight_layout()

        # Cria o diretório para salvar o gráfico, se não existir
        diretorio_graficos = 'data/graficos'
        os.makedirs(diretorio_graficos, exist_ok=True)
        plt.savefig(f'{diretorio_graficos}/comparacao_tempos_multiplas_linhas.png')
        plt.show()

    except Exception as e:
        print(f"❌ Erro ao gerar gráficos: {e}")

if __name__ == "__main__":
    caminho_csv_tempo = 'data/relatorios/relatorio_eficiencia_tempo.csv'

    gerar_graficos_barras_tempo(caminho_csv_tempo)
    gerar_graficos_pontos_tempo(caminho_csv_tempo)