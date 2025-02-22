import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

# Nome do arquivo CSV
CSV_FILE = "data/relatorios/relatorio_2025-02-22.csv"
PDF_FILE = "data/relatorios/relatorio_completo.pdf"

def ler_csv():
    """
    Lê o arquivo CSV e retorna uma lista de dicionários com as informações.
    """
    relatorios = []
    try:
        with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                relatorios.append(row)
    except FileNotFoundError:
        print(f"⚠️ Arquivo CSV não encontrado: {CSV_FILE}")
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo CSV: {e}")
    return relatorios

def gerar_pdf(relatorios):
    """
    Gera um PDF com base nos dados extraídos do arquivo CSV.
    """
    try:
        # Cria o PDF com o formato A4
        doc = SimpleDocTemplate(PDF_FILE, pagesize=letter)
        elementos = []

        # Título do PDF
        styles = getSampleStyleSheet()
        titulo = Paragraph("Relatório Completo - Tarefas e Materiais", styles['Title'])
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        subtitulo = Paragraph(f"Gerado em: {data_geracao}", styles['Normal'])
        
        # Adiciona o título e o subtítulo
        elementos.append(titulo)
        elementos.append(subtitulo)
        elementos.append(Paragraph("<br /><br />", styles['Normal']))  # Espaço entre título e tabela

        # Estilo para permitir quebra de linha nas células
        style_normal = styles['Normal']
        style_normal.wordWrap = 'LTR'  # Permite quebra de linha
        style_normal.fontName = 'Helvetica'
        style_normal.fontSize = 10
        style_normal.leading = 12
        style_normal.alignment = 1  # 0=Esquerda, 1=Centro, 2=Direita

        # Cabeçalho da Tabela
        tabela_dados = [[
            Paragraph("Horário de Início", style_normal),
            Paragraph("Tarefa", style_normal),
            Paragraph("Nome do Cliente", style_normal),
            Paragraph("Horário de Fim", style_normal),
            Paragraph("Material Gasto", style_normal)
        ]]

        # Adiciona os dados do CSV
        for relatorio in relatorios:
            tabela_dados.append([
                Paragraph(relatorio["Horário de Início"], style_normal),
                Paragraph(relatorio["Tarefa"], style_normal),
                Paragraph(relatorio["Nome do Cliente"], style_normal),
                Paragraph(relatorio["Horário de Fim"], style_normal),
                Paragraph(relatorio["Material Gasto"], style_normal)
            ])

        # Criação da Tabela
        tabela = Table(tabela_dados, colWidths=[100, 100, 150, 100, 150])  # Ajuste das larguras das colunas
        tabela.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Cabeçalho em preto
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinhamento centralizado
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Cabeçalho em negrito
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding abaixo do cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Cor de fundo do cabeçalho
            ('GRID', (0, 0), (-1, -1), 0.5, (0, 0, 0)),  # Adicionar bordas
            ('LINEBEFORE', (0, 0), (0, -1), 0.5, (0, 0, 0)),  # Bordas à esquerda
            ('LINEAFTER', (-1, 0), (-1, -1), 0.5, (0, 0, 0)),  # Bordas à direita
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alinhamento vertical no topo
            ('LEFTPADDING', (0, 0), (-1, -1), 4),  # Espaço interno esquerdo
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),  # Espaço interno direito
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [0xFFFFFF, 0xf2f2f2]),  # Zebrado opcional
        ]))

        # Adiciona a tabela ao documento
        elementos.append(tabela)

        # Gera o PDF
        doc.build(elementos)

        print(f"✅ Relatório gerado com sucesso! PDF salvo em: {PDF_FILE}")

    except Exception as e:
        print(f"❌ Erro ao gerar o PDF: {e}")

def main():
    """
    Função principal para gerar o relatório completo em PDF a partir do arquivo CSV.
    """
    relatorios = ler_csv()
    if relatorios:
        gerar_pdf(relatorios)
    else:
        print("⚠️ Nenhum dado disponível para gerar o relatório.")

if __name__ == "__main__":
    main()
