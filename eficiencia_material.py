import csv
import json
import openai
from keys import chave_openai
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Configuração da API
openai.api_key = chave_openai

# Tabela de material esperado para cada tarefa (valor em minutos ou unidade definida)
TABELA_MATERIAL_ESPERADO_POR_METRO_QUADRADO = {
    "Pintura Eletrostática": 40,
    "Colagem de Cola Mel": 20,
    "Corte de Isopor": 33,
    "Colagem de Filme (Normal)": 40,
    "Colagem de Filme (Ultra)": 50,
    "Carregamento": 5
}

def extrair_info_material(tarefa_text, material_gasto_text):
    """
    Utiliza a API do GPT para normalizar a tarefa e extrair o valor numérico do material gasto.
    Retorna um tuple (tarefa_normalizada, material_usado) onde:
      - tarefa_normalizada: string, possivelmente ajustada para corresponder a uma das chaves da tabela.
      - material_usado: float com o valor extraído.
    """
    prompt = (
        "Você é um assistente que extrai informações numéricas e normaliza nomes de tarefas. "
        "A partir dos dados a seguir, extraia e retorne um JSON com as seguintes chaves:\n"
        " - tarefa: a tarefa normalizada (deve ser uma das opções: "
        f"{', '.join(TABELA_MATERIAL_ESPERADO_POR_METRO_QUADRADO.keys())})\n"
        " - material_usado: o valor numérico referente ao material gasto (em minutos ou unidade definida).\n\n"
        f"Tarefa: {tarefa_text}\n"
        f"Material Gasto: {material_gasto_text}\n\n"
        "Responda apenas com o JSON."
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que extrai informações numéricas de textos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        resposta_texto = response["choices"][0]["message"]["content"].strip()
        dados = json.loads(resposta_texto)
        tarefa_normalizada = dados.get("tarefa", tarefa_text)
        material_usado = float(dados.get("material_usado", 0))
    except Exception as e:
        print(f"Erro ao extrair info via GPT: {e}")
        tarefa_normalizada = tarefa_text
        try:
            material_usado = float(material_gasto_text)
        except Exception:
            material_usado = 0
    return tarefa_normalizada, material_usado

def gerar_pdf_material(dados, caminho_pdf):
    """Gera um PDF a partir dos dados de eficiência de material."""
    try:
        pdf = SimpleDocTemplate(caminho_pdf, pagesize=letter)
        # Cabeçalhos da tabela
        cabecalhos = ["Etapa", "Material Usado", "Material Esperado", "Diferença de Material", "Status"]
        
        # Prepara os dados para a tabela
        dados_tabela = [cabecalhos]
        for item in dados:
            linha = [
                item["Etapa"],
                item["Material Usado"],
                item["Material Esperado"],
                item["Diferença de Material"],
                item["Status"]
            ]
            dados_tabela.append(linha)

        tabela = Table(dados_tabela)
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

        pdf.build([tabela])
        print(f"✅ PDF gerado com sucesso: {caminho_pdf}")
    except Exception as e:
        print(f"❌ Erro ao gerar o PDF: {e}")

def calcular_eficiencia_material(caminho_csv):
    """
    Calcula a eficiência do material usado com base no arquivo CSV e na tabela de material esperado.
    Utiliza a API do GPT para extrair e normalizar as informações de 'Tarefa' e 'Material Gasto'.
    """
    resultados = []

    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print("Cabeçalhos do CSV:", reader.fieldnames)  # Debug: mostra os cabeçalhos do CSV

        for linha in reader:
            tarefa_text = linha.get('Tarefa')
            material_gasto_text = linha.get('Material Gasto')
            print(f"\nProcessando tarefa: {tarefa_text}")

            # Extrai e normaliza informações usando a API do GPT
            tarefa_normalizada, material_usado = extrair_info_material(tarefa_text, material_gasto_text)
            print(f"Tarefa normalizada: {tarefa_normalizada}, Material Usado: {material_usado}")

            if tarefa_normalizada in TABELA_MATERIAL_ESPERADO_POR_METRO_QUADRADO:
                material_esperado = TABELA_MATERIAL_ESPERADO_POR_METRO_QUADRADO[tarefa_normalizada]
                diferenca_material = material_usado - material_esperado
                status = "Verde" if diferenca_material <= 0 else "Vermelho"
            else:
                material_esperado = "(a definir)"
                diferenca_material = "(a definir)"
                status = "(Verde/Vermelho)"
            
            resultados.append({
                "Etapa": tarefa_normalizada,
                "Material Usado": material_usado,
                "Material Esperado": material_esperado,
                "Diferença de Material": diferenca_material,
                "Status": status
            })

    return resultados

def salvar_csv_material(resultados, caminho_csv):
    """Salva os resultados de eficiência de material em um arquivo CSV."""
    try:
        with open(caminho_csv, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = resultados[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(resultados)

        print(f"✅ Relatório salvo com sucesso em CSV: {caminho_csv}")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo CSV: {e}")

def gerar_relatorio_eficiencia_material():
    """
    Gera o relatório de eficiência de material:
      - Lê o CSV com as colunas: Horário de Início, Tarefa, Nome do Cliente, Horário de Fim, Material Gasto.
      - Usa a API do GPT para extrair e normalizar as informações de 'Tarefa' e 'Material Gasto',
        comparando o valor extraído com o valor esperado (da tabela de referência).
      - Gera um relatório (em PDF e CSV) com os resultados.
    """
    caminho_csv = "data/relatorios/relatorio_2025-02-24.csv"  
    PDF_FILE = "data/relatorios/relatorio_eficiencia_material.pdf"
    CSV_FILE = "data/relatorios/relatorio_eficiencia_material.csv"

    relatorios = calcular_eficiencia_material(caminho_csv)
    print("Relatórios gerados:", relatorios)  # Debug: mostra os relatórios gerados

    if relatorios:
        try:
            gerar_pdf_material(relatorios, PDF_FILE)
        except Exception as e:
            print(f"❌ Erro ao gerar o PDF: {e}")
        salvar_csv_material(relatorios, CSV_FILE)
    else:
        print("⚠️ Nenhum dado disponível para gerar o relatório de eficiência de material.")

if __name__ == "__main__":
    gerar_relatorio_eficiencia_material()
