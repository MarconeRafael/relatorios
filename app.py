from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import main  # Importa sua lógica de processamento já existente
import transcrever_audio  # Supondo que esta função aceite um arquivo de áudio

app = Flask(__name__)

# Defina os diretórios para servir gráficos e relatórios dinamicamente
app.config['GRAPHIQUE_DIR'] = os.path.join(os.getcwd(), 'data', 'graficos')
app.config['RELATORIO_DIR'] = os.path.join(os.getcwd(), 'data', 'relatorios')
app.config['AUDIOS_DIR'] = os.path.join(os.getcwd(), 'data', 'audios')

# Tela principal com botão de gravação, transcrição e navegação
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint para processar o áudio enviado pelo navegador
@app.route("/processar_audio", methods=["POST"])
def processar_audio():
    try:
        if "audio_data" not in request.files:
            return jsonify({"error": "Nenhum arquivo de áudio enviado."}), 400

        audio_file = request.files["audio_data"]

        # Salvar o arquivo temporariamente para processamento
        temp_audio_path = os.path.join(app.config['AUDIOS_DIR'], audio_file.filename)
        os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
        audio_file.save(temp_audio_path)

        # Chama a função de transcrição (adaptar se necessário)
        transcricao = transcrever_audio.transcrever_audio(temp_audio_path)

        # Retornar a transcrição para a interface
        return jsonify({"transcricao": transcricao})
    except Exception as e:
        return jsonify({"error": f"Erro: {e}"}), 500

# Endpoint para o processamento ao clicar em "Concluir"
@app.route("/concluir", methods=["POST"])
def concluir():
    try:
        # Obtém os textos transcritos do corpo da requisição
        dados = request.get_json()
        texto_inicial = dados.get('texto_inicial')
        texto_final = dados.get('texto_final')

        # Verifica se os textos foram fornecidos
        if not texto_inicial or not texto_final:
            return jsonify({"success": False, "error": "Textos de início e fim são obrigatórios."}), 400

        # Chama a função processar_textos do main.py
        main.processar_textos(texto_inicial, texto_final)

        # Retorna uma resposta de sucesso
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Tela de Relatórios
@app.route("/relatorios")
def relatorios():
    data_atual = "2025-02-22"  # Substitua por lógica dinâmica se necessário
    pdf_path = f"data/relatorios/relatorio_completo_{data_atual}.pdf"

    relatorio_pdf = "relatorio_completo_2025-03-05.pdf"
    relatorio_eficiencia_csv = "relatorio_eficiencia_material.csv"
    relatorio_eficiencia_pdf = "relatorio_eficiencia.pdf"

    return render_template("relatorios.html", 
                           pdf_path=pdf_path,
                           relatorio_pdf=relatorio_pdf,
                           relatorio_eficiencia_csv=relatorio_eficiencia_csv,
                           relatorio_eficiencia_pdf=relatorio_eficiencia_pdf)

# Tela de Gráficos
@app.route("/graficos")
def graficos():
    return render_template("graficos.html")

# Rota para servir os gráficos diretamente
@app.route('/graficos/<path:filename>')
def serve_graphics(filename):
    return send_from_directory(app.config['GRAPHIQUE_DIR'], filename)

# Rota para servir os relatórios diretamente
@app.route('/relatorios/<path:filename>')
def serve_report(filename):
    return send_from_directory(app.config['RELATORIO_DIR'], filename)

if __name__ == "__main__":
    app.run(debug=True)