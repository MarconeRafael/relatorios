import csv
from datetime import datetime
import openai
from keys import chave_openai  # Certifique-se de que a chave da API está disponível
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def gerar_pdf_tempo(dados, caminho_pdf):
    """Gera um PDF a partir dos dados de eficiência."""
    try:
        # Cria um documento PDF
        pdf = SimpleDocTemplate(caminho_pdf, pagesize=letter)

        # Cabeçalhos da tabela
        cabecalhos = ["Etapa", "Tempo Gasto (min)", "Tempo Esperado (min)", "Diferença de Tempo", "Status"]
        
        # Prepara os dados para a tabela
        dados_tabela = [cabecalhos]  # Adiciona os cabeçalhos
        for item in dados:
            linha = [item["Etapa"],
                     item["Tempo Gasto (min)"],
                     item["Tempo Esperado (min)"],
                     item["Diferença de Tempo"],
                     item["Status"]]
            dados_tabela.append(linha)

        # Cria uma tabela
        tabela = Table(dados_tabela)

        # Estilo da tabela
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        tabela.setStyle(estilo)

        # Adiciona a tabela ao documento
        pdf.build([tabela])
        print(f"✅ PDF gerado com sucesso: {caminho_pdf}")
    except Exception as e:
        print(f"❌ Erro ao gerar o PDF: {e}")


# Definindo os parâmetros de tempo esperado para cada tarefa em minutos
# Definindo os parâmetros de tempo esperado para cada tarefa em minutos
TABELA_TEMPO_ESPERADO = {
    "Aplicação do Filme": 0.3,                     # 18 segundos / 60 = 0.3 minutos
    "Corte do EPS (CNC – Corte Reto)": 5,          # 300 segundos / 60 = 5 minutos
    "Corte do EPS (CNC – Corte com Esquadro)": 8.75, # 525 segundos / 60 = 8.75 minutos
    "Pintura Eletrostática": 1.2,                  # 72 segundos / 60 = 1.2 minutos
    "Montagem de Telhas": 0.8                      # 48 segundos / 60 = 0.8 minutos
}



def calcular_eficiencia_tempo(caminho_csv):
    """Calcula a eficiência com base no arquivo CSV e na tabela de tempo esperado."""
    resultados = []

    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        print("Cabeçalhos do CSV:", reader.fieldnames)  # Debug: mostra os cabeçalhos do CSV
        
        for linha in reader:
            tarefa = linha['Tarefa']
            tempo_inicial = linha['Horário de Início']
            tempo_final = linha['Horário de Fim']
            print(f"\nProcessando tarefa: {tarefa}")  # Debug: mostra a tarefa sendo processada
            
            tempo_gasto = calcular_tempo_gasto_tempo(tempo_inicial, tempo_final)
            print(f"Tempo Gasto: {tempo_gasto} minutos")  # Debug: mostra tempo gasto
            
            if tarefa in TABELA_TEMPO_ESPERADO:
                tempo_esperado = TABELA_TEMPO_ESPERADO[tarefa]
                print(f"Tempo Esperado para '{tarefa}': {tempo_esperado} minutos")  # Debug: mostra tempo esperado
                
                if tempo_esperado is not None:
                    diferenca_tempo = tempo_gasto - tempo_esperado
                    status = "Verde" if diferenca_tempo <= 0 else "Vermelho"
                else:
                    diferenca_tempo = "(a definir)"
                    status = "(Verde/Vermelho)"
                
                resultados.append({
                    "Etapa": tarefa,
                    "Tempo Gasto (min)": tempo_gasto,
                    "Tempo Esperado (min)": tempo_esperado if tempo_esperado is not None else "(a definir)",
                    "Diferença de Tempo": diferenca_tempo,
                    "Status": status
                })

    return resultados

def salvar_csv_tempo(resultados, caminho_csv):
    """Salva os resultados de eficiência em um arquivo CSV."""
    try:
        with open(caminho_csv, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = resultados[0].keys()  # Usa as chaves do primeiro dicionário como cabeçalhos
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()  # Escreve o cabeçalho
            writer.writerows(resultados)  # Escreve as linhas de dados

        print(f"✅ Relatório salvo com sucesso em CSV: {caminho_csv}")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo CSV: {e}")

def formatar_horario_tempo(horario):
    """Formata o horário para o formato 'YYYY-MM-DD HH:MM:SS'."""
    data_padrao = "2025-02-22"  # Data padrão, ajuste conforme necessário
    try:
        # Troca 'h' por ':' e remove espaços adicionais
        horario = horario.replace('h', ':').strip().rstrip('.')  # Remove ponto no final
        
        # Verifica se o horário está no formato correto
        if ':' not in horario:
            raise ValueError("Formato de horário inválido. Use 'HH:MM'.")

        # Adiciona a data padrão e os segundos ao horário
        horario_formatado = f"{data_padrao} {horario}:00"  # Adicionando ':00' para os segundos
        
        # Valida o formato
        datetime.strptime(horario_formatado, "%Y-%m-%d %H:%M:%S")  # Para validar o formato
        return horario_formatado
    except ValueError as e:
        print(f"Erro ao formatar o horário: {horario}. {e}")
        return None  # Retorna None se houver erro

def calcular_tempo_gasto_tempo(horario_inicio, horario_fim):
    """Calcula o tempo gasto entre dois horários formatados."""
    inicio_formatado = formatar_horario_tempo(horario_inicio)
    fim_formatado = formatar_horario_tempo(horario_fim)

    # Verifica se os horários foram formatados corretamente
    if not inicio_formatado:
        print(f"Erro ao formatar o horário de início: {horario_inicio}")
        return 0  # Retorna 0 se houver erro na formatação
    if not fim_formatado:
        print(f"Erro ao formatar o horário de fim: {horario_fim}")
        return 0  # Retorna 0 se houver erro na formatação

    try:
        # Converte os horários formatados para datetime
        inicio = datetime.strptime(inicio_formatado, "%Y-%m-%d %H:%M:%S")
        fim = datetime.strptime(fim_formatado, "%Y-%m-%d %H:%M:%S")

        # Calcula o tempo gasto em minutos
        tempo_gasto = (fim - inicio).total_seconds() / 60  # Converte para minutos

        # Verifica se o tempo gasto é negativo (o que indicaria um erro)
        if tempo_gasto < 0:
            print(f"Erro: O tempo gasto é negativo. Horário de início: {inicio_formatado}, Horário de fim: {fim_formatado}")
            return 0  # Retorna 0 se o tempo gasto for negativo

        print(f"Tempo Gasto calculado: {tempo_gasto} minutos")
        return tempo_gasto
    except Exception as e:
        print(f"Erro ao calcular o tempo gasto: {e}")
        return 0  # Retorna 0 se houver erro

def gerar_relatorio_eficiencia_tempo(caminho_csv):
    """Gera o relatório de eficiência e chama a função para gerar o PDF e salvar em CSV."""
    caminho_csv = caminho_csv
    PDF_FILE = "data/relatorios/relatorio_eficiencia.pdf"
    CSV_FILE = "data/relatorios/relatorio_eficiencia_tempo.csv"  # Novo caminho para o CSV

    relatorios = calcular_eficiencia_tempo(caminho_csv)
    print("Relatórios gerados:", relatorios)  # Debug: mostra os relatórios gerados

    if relatorios:
        try:
            gerar_pdf_tempo(relatorios, PDF_FILE)
        except Exception as e:
            print(f"❌ Erro ao gerar o PDF: {e}")
        salvar_csv_tempo(relatorios, CSV_FILE)  # Salva em CSV
    else:
        print("⚠️ Nenhum dado disponível para gerar o relatório de eficiência.")

if __name__ == "__main__":
    caminho_csv = "data/relatorios/relatorio_2025-02-24.csv"
    gerar_relatorio_eficiencia_tempo(caminho_csv)
