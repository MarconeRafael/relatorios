from transcrever_audio import transcrever_audio
from inicio import organiza_inicio
from fim import organiza_fim
from gerar_pdf import gerar_pdf, ler_csv
from graficos_tempo import gerar_graficos_barras_tempo, gerar_graficos_pontos_tempo
from graficos_material import gerar_graficos_barras_material, gerar_graficos_pontos_material
import os
import shutil
from datetime import datetime, timedelta
from eficiencia_tempo import gerar_relatorio_eficiencia_tempo, salvar_csv_tempo
from eficiencia_material import gerar_relatorio_eficiencia_material, salvar_csv_material

AUDIO_DIR = "data/audios"
TEMP_DIR = "data/temp_audio"
DELETE_AFTER_HOURS = 24  # Tempo para deletar os arquivos após 24 horas

def mover_arquivos_para_temp():
    """
    Move todos os arquivos da pasta 'audios' para a pasta temporária.
    """
    try:
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        
        for arquivo in os.listdir(AUDIO_DIR):
            caminho_arquivo = os.path.join(AUDIO_DIR, arquivo)
            if os.path.isfile(caminho_arquivo):
                shutil.move(caminho_arquivo, TEMP_DIR)
                print(f"📦 Arquivo {arquivo} movido para a pasta temporária.")
    except Exception as e:
        print(f"❌ Erro ao mover arquivos: {e}")

def deletar_arquivos_temp():
    """
    Deleta todos os arquivos na pasta temporária após 24 horas.
    """
    try:
        tempo_atual = datetime.now()
        for arquivo in os.listdir(TEMP_DIR):
            caminho_arquivo = os.path.join(TEMP_DIR, arquivo)
            if os.path.isfile(caminho_arquivo):
                tempo_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                if tempo_atual - tempo_modificacao > timedelta(hours=DELETE_AFTER_HOURS):
                    os.remove(caminho_arquivo)
                    print(f"🗑️ Arquivo {arquivo} deletado da pasta temporária após 24 horas.")
    except Exception as e:
        print(f"❌ Erro ao deletar arquivos temporários: {e}")

def main():
    """
    Função principal para processar os arquivos de áudio, transcrever,
    organizar os dados e gerar os relatórios.
    
    Ordem de execução:
    1. Transcrição dos áudios.
    2. Processamento do relatório de início.
    3. Processamento do relatório de fim.
    4. Geração do relatório completo (CSV e PDF).
    5. Geração do relatório de eficiência de tempo.
    6. Geração do relatório de eficiência de material.
    7. Geração dos gráficos.
    """
    # Definir os caminhos dos arquivos de áudio
    path_inicio = "data/audios/WhatsApp Ptt 2025-02-22 at 08.54.35.ogg"
    path_final = "data/audios/WhatsApp Ptt 2025-02-22 at 09.39.32.ogg"
    
    try:
        print(f"📂 Processando o arquivo de início: {path_inicio}")
        print(f"📂 Processando o arquivo final: {path_final}")

        # Transcrever os áudios
        texto_inicial = transcrever_audio(path_inicio)
        texto_final = transcrever_audio(path_final)

        #texto_inicial = "Às 8 horas, início da tarefa montagem de Telhas do cliente Anderson"
        #texto_final = "Tarefa de início da tarefa montagem de Telhas do cliente Anderson. foram feitos 60 metros, foi gasto 6 e terminou na hora 9 e 35"
        
        if not texto_inicial:
            print("⚠️ Nenhum texto foi transcrito do áudio de início.")
            return
        if not texto_final:
            print("⚠️ Nenhum texto foi transcrito do áudio final.")
            return
        
        # Processar as transcrições: Início e Fim
        relatorio_inicio = organiza_inicio(texto_inicial)
        relatorio_final = organiza_fim(texto_final)
        
        print("✅ Relatório de início gerado:")
        print(relatorio_inicio)
        print("✅ Relatório de fim gerado:")
        print(relatorio_final)
        
        # Definir o caminho do relatório principal com base na data atual
        data_atual = datetime.now().strftime("%Y-%m-%d")
        csv_principal = f"data/relatorios/relatorio_{data_atual}.csv"
        pdf_principal = f"data/relatorios/relatorio_completo_{data_atual}.pdf"
        print(f"\n\n\n\csv_principal:\n{csv_principal}\n\n\n")
        # Gerar o relatório completo em PDF a partir do CSV principal
        relatorios_completos = ler_csv(csv_principal)
        if relatorios_completos:
            gerar_pdf(relatorios_completos, pdf_principal)
            print(f"✅ Relatório completo gerado em PDF: {pdf_principal}")
        else:
            print("⚠️ Nenhum dado disponível para gerar o relatório completo.")
        
        # Geração do relatório de eficiência de tempo
        print("ENtrando em eficiencia de tempo")
        relatorios_tempo = gerar_relatorio_eficiencia_tempo(csv_principal)
        csv_eficiencia_tempo = "data/relatorios/relatorio_eficiencia_tempo.csv"
        """
        if relatorios_tempo:
            salvar_csv_tempo(relatorios_tempo, csv_eficiencia_tempo)
            print(f"✅ Relatório de eficiência de tempo salvo em CSV: {csv_eficiencia_tempo}")
        else:
            print("⚠️ Nenhum dado disponível para gerar o relatório de eficiência de tempo.")
        """
        print("Saindo de eficiencia de tempo")
        
        
        # Geração do relatório de eficiência de material
        relatorios_material = gerar_relatorio_eficiencia_material(csv_principal)
        csv_eficiencia_material = "data/relatorios/relatorio_eficiencia_material.csv"
        """
        if relatorios_material:
            salvar_csv_material(relatorios_material, csv_eficiencia_material)
            print(f"✅ Relatório de eficiência de material salvo em CSV: {csv_eficiencia_material}")
        else:
            print("⚠️ Nenhum dado disponível para gerar o relatório de eficiência de material.")
        """
        
        # Gerar os gráficos a partir dos relatórios de eficiência
        gerar_graficos_barras_tempo(csv_eficiencia_tempo)
        gerar_graficos_pontos_tempo(csv_eficiencia_tempo)
        gerar_graficos_pontos_material(csv_eficiencia_material)
        gerar_graficos_barras_material(csv_eficiencia_material)
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")

if __name__ == "__main__":
    # Mover arquivos para a pasta temporária à meia-noite
    horario_atual = datetime.now()
    if horario_atual.hour == 0 and horario_atual.minute == 0:
        mover_arquivos_para_temp()
    
    # Deletar arquivos na pasta temporária após 24 horas
    deletar_arquivos_temp()
    
    # Processar os áudios e gerar os relatórios
    main()
