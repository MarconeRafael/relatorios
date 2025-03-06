from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import shutil
import time
from datetime import datetime, timedelta

# Importações dos módulos de processamento e geração de relatórios
from transcrever_audio import transcrever_audio
from inicio import organiza_inicio
from fim import organiza_fim
from gerar_pdf import gerar_pdf, ler_csv
from graficos_tempo import gerar_graficos_barras_tempo, gerar_graficos_pontos_tempo
from graficos_material import gerar_graficos_barras_material, gerar_graficos_pontos_material
from eficiencia_tempo import gerar_relatorio_eficiencia_tempo, salvar_csv_tempo
from eficiencia_material import gerar_relatorio_eficiencia_material, salvar_csv_material

# Diretórios e configurações
AUDIO_DIR = "data/audios"
TEMP_DIR = "data/temp_audio"
DELETE_AFTER_HOURS = 24  # Tempo para deletar os arquivos após 24 horas

# Instância do Flask e configuração dos diretórios de gráficos e relatórios
app = Flask(__name__)
app.config['GRAPHIQUE_DIR'] = os.path.join(os.getcwd(), 'data', 'graficos')
app.config['RELATORIO_DIR'] = os.path.join(os.getcwd(), 'data', 'relatorios')

# =============================================================================
# Funções para gerenciamento dos arquivos de áudio e geração de relatórios
# =============================================================================

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
        if os.path.exists(TEMP_DIR):
            for arquivo in os.listdir(TEMP_DIR):
                caminho_arquivo = os.path.join(TEMP_DIR, arquivo)
                if os.path.isfile(caminho_arquivo):
                    tempo_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                    if tempo_atual - tempo_modificacao > timedelta(hours=DELETE_AFTER_HOURS):
                        os.remove(caminho_arquivo)
                        print(f"🗑️ Arquivo {arquivo} deletado da pasta temporária após 24 horas.")
    except Exception as e:
        print(f"❌ Erro ao deletar arquivos temporários: {e}")

def wait_for_audio_files(timeout=60):
    """
    Aguarda até que os arquivos de áudio de 'início' e 'fim' estejam presentes na pasta AUDIO_DIR.
    Timeout em segundos.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        arquivos_audio = os.listdir(AUDIO_DIR)
        path_inicio = ""
        path_final = ""
        for arquivo in arquivos_audio:
            lower = arquivo.lower()
            if "inicio" in lower:
                path_inicio = os.path.join(AUDIO_DIR, arquivo)
            elif "fim" in lower:
                path_final = os.path.join(AUDIO_DIR, arquivo)
        if path_inicio and path_final:
            return path_inicio, path_final
        time.sleep(1)
    return None, None

def processar_relatorios():
    """
    Processa os arquivos de áudio, transcreve, organiza os dados e gera os relatórios e gráficos.
    
    Ordem de execução:
      1. Aguarda a chegada dos arquivos de áudio (início e fim).
      2. Transcreve os áudios.
      3. Processa os relatórios de início e fim.
      4. Gera o relatório completo (CSV e PDF).
      5. Gera os relatórios de eficiência.
      6. Gera os gráficos correspondentes.
    
    Retorna um dicionário com o resultado do processamento.
    """
    # Deleta arquivos antigos na pasta temporária
    deletar_arquivos_temp()
    
    print("⏳ Aguardando arquivos de áudio (início e fim)...")
    path_inicio, path_final = wait_for_audio_files(timeout=60)
    if not path_inicio or not path_final:
        error_msg = "⚠️ Não foi encontrado o arquivo de início ou de fim na pasta de áudios dentro do tempo esperado."
        print(error_msg)
        return {"error": error_msg}
    
    try:
        print(f"📂 Processando o arquivo de início: {path_inicio}")
        print(f"📂 Processando o arquivo final: {path_final}")

        # Transcreve os áudios
        texto_inicial = transcrever_audio(path_inicio)
        texto_final = transcrever_audio(path_final)

        if not texto_inicial:
            error_msg = "⚠️ Nenhum texto foi transcrito do áudio de início."
            print(error_msg)
            return {"error": error_msg}
        if not texto_final:
            error_msg = "⚠️ Nenhum texto foi transcrito do áudio final."
            print(error_msg)
            return {"error": error_msg}
        
        # Organiza as transcrições
        relatorio_inicio = organiza_inicio(texto_inicial)
        relatorio_final = organiza_fim(texto_final)
        
        print("✅ Relatório de início gerado:")
        print(relatorio_inicio)
        print("✅ Relatório de fim gerado:")
        print(relatorio_final)
        
        # Define os caminhos para o relatório principal com base na data atual
        data_atual = datetime.now().strftime("%Y-%m-%d")
        csv_principal = f"data/relatorios/relatorio_{data_atual}.csv"
        pdf_principal = f"data/relatorios/relatorio_completo_{data_atual}.pdf"
        print(f"\n\ncsv_principal:\n{csv_principal}\n")
        
        # Gera o relatório completo em PDF a partir do CSV principal
        relatorios_completos = ler_csv(csv_principal)
        if relatorios_completos:
            gerar_pdf(relatorios_completos, pdf_principal)
            print(f"✅ Relatório completo gerado em PDF: {pdf_principal}")
        else:
            print("⚠️ Nenhum dado disponível para gerar o relatório completo.")
        
        # Geração dos relatórios de eficiência
        gerar_relatorio_eficiencia_tempo(csv_principal)
        csv_eficiencia_tempo = "data/relatorios/relatorio_eficiencia_tempo.csv"
        
        gerar_relatorio_eficiencia_material(csv_principal)
        csv_eficiencia_material = "data/relatorios/relatorio_eficiencia_material.csv"
        
        # Geração dos gráficos a partir dos relatórios de eficiência
        gerar_graficos_barras_tempo(csv_eficiencia_tempo)
        gerar_graficos_pontos_tempo(csv_eficiencia_tempo)
        gerar_graficos_pontos_material(csv_eficiencia_material)
        gerar_graficos_barras_material(csv_eficiencia_material)
        
        return {
            "message": "Relatórios e gráficos gerados com sucesso.",
            "pdf_principal": pdf_principal,
            "csv_principal": csv_principal,
            "csv_eficiencia_tempo": csv_eficiencia_tempo,
            "csv_eficiencia_material": csv_eficiencia_material
        }
        
    except Exception as e:
        error_msg = f"❌ Erro durante a execução: {e}"
        print(error_msg)
        return {"error": error_msg}

# =============================================================================
# Rotas da aplicação Flask
# =============================================================================

# Página principal com interface de gravação e navegação
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint para processar o áudio enviado pelo navegador
@app.route("/processar_audio", methods=["POST"])
def processar_audio_route():
    try:
        if "audio_data" not in request.files:
            return jsonify({"error": "Nenhum arquivo de áudio enviado."}), 400

        audio_file = request.files["audio_data"]

        # Salva o arquivo na pasta de áudios para posterior processamento
        temp_audio_path = os.path.join(AUDIO_DIR, audio_file.filename)
        os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
        audio_file.save(temp_audio_path)

        # Chama a função de transcrição
        transcricao = transcrever_audio(temp_audio_path)

        return jsonify({"transcricao": transcricao})
    except Exception as e:
        return jsonify({"error": f"Erro: {e}"}), 500

# Endpoint para processar os relatórios (aguarda arquivos 'início' e 'fim')
@app.route("/processar_relatorios", methods=["POST"])
def processar_relatorios_route():
    resultado = processar_relatorios()
    if "error" in resultado:
        return jsonify(resultado), 500
    return jsonify(resultado)

# Página de relatórios
@app.route("/relatorios")
def relatorios():
    data_atual = datetime.now().strftime("%Y-%m-%d")
    pdf_path = f"data/relatorios/relatorio_completo_{data_atual}.pdf"

    # Os nomes dos arquivos podem ser adaptados conforme a lógica desejada
    relatorio_pdf = f"relatorio_completo_{data_atual}.pdf"
    relatorio_eficiencia_csv = "relatorio_eficiencia_material.csv"
    relatorio_eficiencia_pdf = "relatorio_eficiencia.pdf"

    return render_template("relatorios.html", 
                           pdf_path=pdf_path,
                           relatorio_pdf=relatorio_pdf,
                           relatorio_eficiencia_csv=relatorio_eficiencia_csv,
                           relatorio_eficiencia_pdf=relatorio_eficiencia_pdf)

# Página de gráficos
@app.route("/graficos")
def graficos():
    return render_template("graficos.html")

# Rota para servir os arquivos de gráficos
@app.route('/graficos/<path:filename>')
def serve_graphics(filename):
    return send_from_directory(app.config['GRAPHIQUE_DIR'], filename)

# Rota para servir os arquivos de relatórios
@app.route('/relatorios/<path:filename>')
def serve_report(filename):
    return send_from_directory(app.config['RELATORIO_DIR'], filename)

# =============================================================================
# Execução da aplicação Flask
# =============================================================================
if __name__ == "__main__":
    # Exemplo: mover arquivos para a pasta temporária à meia-noite
    horario_atual = datetime.now()
    if horario_atual.hour == 0 and horario_atual.minute == 0:
        mover_arquivos_para_temp()
    
    app.run(debug=True)
