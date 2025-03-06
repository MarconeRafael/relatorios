import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.lines as mlines
import numpy as np

def gerar_graficos_barras_material(caminho_csv):
    caminho_csv =  caminho_csv

    """Gera gráfico de barras usando Material Esperado, Material Usado, Diferença de Material e anota Status."""
    try:
        # Lê os dados do CSV
        dados = pd.read_csv(caminho_csv)

        # Cria o diretório para os gráficos, se não existir
        diretorio_graficos = 'data/graficos'
        os.makedirs(diretorio_graficos, exist_ok=True)

        # Configura a posição de cada grupo de barras
        n = len(dados)
        x = np.arange(n)
        width = 0.25

        fig, ax = plt.subplots(figsize=(12, 6))

        # Plota "Material Esperado" na primeira coluna (posição x - width) com cor azul
        ax.bar(x - width, dados["Material Esperado"], width,
               label='Material Esperado', color='blue')

        # Plota "Material Usado" na segunda coluna (posição x) com cor preta
        ax.bar(x, dados["Material Usado"], width,
               label='Material Usado', color='black')

        # Define as cores para "Diferença de Material": vermelho se positivo, verde se negativo
        cores_diferenca = ['red' if v > 0 else 'green' for v in dados["Diferença de Material"]]
        # Plota "Diferença de Material" na terceira coluna (posição x + width)
        ax.bar(x + width, dados["Diferença de Material"], width,
               label='Diferença de Material', color=cores_diferenca)

        # Anota o status para cada etapa, posicionando o texto acima do maior valor da barra
        for i, row in dados.iterrows():
            max_val = max(row["Material Esperado"], row["Material Usado"], row["Diferença de Material"])
            ax.text(x[i], max_val + 0.05 * max_val, str(row["Status"]),
                    ha='center', va='bottom', fontsize=8)

        # Configurações do gráfico
        ax.set_title('Comparação de Material Usado, Material Esperado e Diferença por Etapa')
        ax.set_ylabel('Quantidade de Material')
        ax.set_xlabel('Etapa')
        ax.set_xticks(x)
        ax.set_xticklabels(dados["Etapa"], rotation=45)
        ax.legend(title='Tipo')

        plt.tight_layout()
        plt.savefig(f'{diretorio_graficos}/comparacao_material.png')
        plt.show()

    except Exception as e:
        print(f"❌ Erro ao gerar gráficos de barras: {e}")


def gerar_graficos_pontos_material(caminho_csv):
    caminho_csv =  caminho_csv
    """Gera gráficos de linhas múltiplas para Material Esperado, Material Usado e Diferença de Material."""
    try:
        # Lê os dados do CSV
        dados = pd.read_csv(caminho_csv)

        # Se a coluna 'Diferença de Material' não existir, calcula-a
        if "Diferença de Material" not in dados.columns:
            dados["Diferença de Material"] = dados["Material Usado"] - dados["Material Esperado"]

        # Define o eixo x como índices numéricos e usa as labels de 'Etapa'
        x = np.arange(len(dados))

        # Séries de dados
        material_esperado = dados["Material Esperado"]
        material_usado = dados["Material Usado"]
        diff = dados["Diferença de Material"]

        # Cria a figura
        plt.figure(figsize=(12, 6))

        # Plota Material Esperado em azul
        plt.plot(x, material_esperado, color='blue', marker='o', linestyle='-', label='Material Esperado')

        # Plota Material Usado em preto
        plt.plot(x, material_usado, color='black', marker='o', linestyle='-', label='Material Usado')

        # Função auxiliar para plotar a linha de Diferença com cores conforme o sinal
        def plot_diff_line(x_vals, y_vals):
            start = 0
            for i in range(1, len(x_vals)):
                if (y_vals.iloc[i] >= 0) == (y_vals.iloc[i-1] >= 0):
                    continue
                segment_x = x_vals[start:i]
                segment_y = y_vals.iloc[start:i]
                cor = 'red' if segment_y.iloc[0] >= 0 else 'green'
                plt.plot(segment_x, segment_y, color=cor, marker='o', linestyle='-')
                start = i
            segment_x = x_vals[start:]
            segment_y = y_vals.iloc[start:]
            if not segment_y.empty:
                cor = 'red' if segment_y.iloc[0] >= 0 else 'green'
                plt.plot(segment_x, segment_y, color=cor, marker='o', linestyle='-')

        # Plota a linha de Diferença
        plot_diff_line(x, diff)

        # Configura os rótulos do eixo x com as etapas
        plt.xticks(x, dados['Etapa'], rotation=45)
        plt.xlabel('Etapa')
        plt.ylabel('Quantidade de Material e Diferença')
        plt.title('Comparação: Material Esperado, Material Usado e Diferença de Material')

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
        plt.savefig(f'{diretorio_graficos}/comparacao_material_multiplas_linhas.png')
        plt.show()

    except Exception as e:
        print(f"❌ Erro ao gerar gráficos de pontos: {e}")


if __name__ == "__main__":
    caminho_csv_material = 'data/relatorios/relatorio_eficiencia_material.csv'
    gerar_graficos_barras_material(caminho_csv_material)
    gerar_graficos_pontos_material(caminho_csv_material)
