from transcrever_audio import transcrever_audio
from inico import organiza_inicio
from fim import organiza_fim
from gerar_pdf import gerar_pdf, ler_csv
import os
import shutil
import time
from datetime import datetime, timedelta
from eficiencia import calcular_eficiencia, salvar_csv
AUDIO_DIR = "data/audios"
TEMP_DIR = "data/temp_audio"
DELETE_AFTER_HOURS = 24  # tempo para deletar os arquivos após 24 horas

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
                # Verifica o tempo de modificação do arquivo
                tempo_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                if tempo_atual - tempo_modificacao > timedelta(hours=DELETE_AFTER_HOURS):
                    os.remove(caminho_arquivo)
                    print(f"🗑️ Arquivo {arquivo} deletado da pasta temporária após 24 horas.")
    except Exception as e:
        print(f"❌ Erro ao deletar arquivos temporários: {e}")

def main():
    """
    Função principal para processar o arquivo de áudio, transcrever o texto e organizá-lo em um relatório.
    """
    # Definir os caminhos dos arquivos de áudio
    path_inicio = "data/audios/WhatsApp Ptt 2025-02-22 at 08.54.35.ogg"
    path_final = "data/audios/WhatsApp Ptt 2025-02-22 at 09.39.32.ogg"
    
    try:
        print(f"📂 Processando o arquivo: {path_inicio}")
        print(f"📂 Processando o arquivo: {path_final}")

        # Transcrever áudio
        texto_inicial = transcrever_audio(path_inicio)
        texto_final = transcrever_audio(path_final)
        
        # Verificar se a transcrição foi realizada com sucesso
        if not texto_inicial:
            print("⚠️ Nenhum texto foi transcrito do áudio de início.")
            return
        if not texto_final:
            print("⚠️ Nenhum texto foi transcrito do áudio final.")
            return
        
        # Gerar relatórios
        relatorio_inicio = organiza_inicio(texto_inicial)
        relatorio_final = organiza_fim(texto_final)
        
        # Exibir os relatórios gerados
        print("✅ Relatório inicial gerado com sucesso:")
        print(relatorio_inicio)
        print("✅ Relatório final gerado com sucesso:")
        print(relatorio_final)
        CSV_FILE = "data/relatorios/relatorio_2025-02-24.csv"
        PDF_FILE = "data/relatorios/relatorio_completo.pdf"

        relatorios = ler_csv(CSV_FILE)
        if relatorios:
            gerar_pdf(relatorios, PDF_FILE)
        else:
                print("⚠️ Nenhum dado disponível para gerar o relatório.")
        """Gera o relatório de eficiência e chama a função para gerar o PDF e salvar em CSV."""
        caminho_csv = "data/relatorios/relatorio_2025-02-24.csv"
        PDF_FILE = "data/relatorios/relatorio_eficiencia.pdf"
        CSV_FILE = "data/relatorios/relatorio_eficiencia.csv"  # Novo caminho para o CSV

        relatorios = calcular_eficiencia(caminho_csv)
        print("Relatórios gerados:", relatorios)  # Debug: mostra os relatórios gerados

        if relatorios:
            try:
                gerar_pdf(relatorios, PDF_FILE)
            except Exception as e:
                print(f"❌ Erro ao gerar o PDF: {e}")
            salvar_csv(relatorios, CSV_FILE)  # Salva em CSV
        else:
            print("⚠️ Nenhum dado disponível para gerar o relatório de eficiência.")
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
